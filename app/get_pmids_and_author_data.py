# %%
import asyncio
import nest_asyncio
import requests
import xml.etree.ElementTree as ET
import json
import subprocess
import time
import re
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

# %%
with open('../config.json', 'r') as file:
    config = json.load(file)
ncbi_api_key = config['apiKeys']['ncbi']


# %%
def get_pmids_from_term(api_key: str, term: str):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": 2,  # limit to 2 PMIDs per term to reduce redundancy while also account for cases of missing "affiliation" or "institute" field for the same author
        "api_key": api_key
    }

    # Create a session object
    session = requests.Session()

    # Define retry strategy
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504], method_whitelist=["GET"])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        # Respect the rate limit
        time.sleep(0.1)

        response = session.get(url=url, params=params)

        if response.status_code == 200:
            data = response.json()

            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                idlist = data['esearchresult']['idlist']
            else:
                print(f"The expected 'idlist' for {term} was not found in the response.")
                return []

            if not idlist:
                print(f"No PMIDs found for term: {term}")
                return []
            else:
                # Instead of returning a string of PMIDs, return the list directly
                return idlist
        else:
            print(f"Failed to retrieve search result: {response.status_code}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []


# %%
# Testing:
term = 'Nikolai Kolba'
idlist = get_pmids_from_term(ncbi_api_key, term)
print(idlist)

# %%
rneasy_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/rneasy_20_23.csv')
rneasy_df["FullName"] = rneasy_df.apply(
    lambda row: str(row["FirstName"]) + " " + str(row["LastName"]),
    axis=1
)
author_names = rneasy_df["FullName"].tolist()
print(author_names)


# %%
def process_pmids_from_author_names(api_key: str, author_names: list):
    all_pmids = []

    for name in tqdm(author_names, desc="Getting PMIDS"):
        idlist = get_pmids_from_term(api_key, name)
        all_pmids.extend(idlist)

    return all_pmids


# %%
pmids_list = process_pmids_from_author_names(ncbi_api_key, author_names)

# %%
pmids_df = pd.DataFrame(pmids_list)
pmids_df.to_pickle('./outputs/addresses_from_names/rneasy_pmids.pkl')

# %%
pmids_df = pd.read_pickle('./outputs/addresses_from_names/rneasy_pmids.pkl')
print("PMIDS_DF FROM PICKLE:\n", pmids_df)
pmid_column_dtype = pmids_df.iloc[:, 0].dtype
print(f"The data type of the first column is: {pmid_column_dtype}")
are_all_values_strings = pmids_df.iloc[:, 0].apply(lambda x: isinstance(x, str)).all()
print(f"Are all values in the first column strings? {are_all_values_strings}")


# %%
def query_pubmed(pmids_list: list) -> list:
    """
    Queries the pubmedAuthorAffiliation.py script for authors' affiliations based on PMIDs or DOIs.

    Parameters:
    pmids_list (list): A list of PMID strings

    Returns:
    list: A list of dictionaries.
    """
    script_path = "pubmedAuthorAffiliation/pubmedAuthorAffiliation.py"
    all_author_data = []
    max_retries = 3  # Maximum number of retries
    retry_delay = 5  # Seconds to wait between retries

    for pmid in tqdm(pmids_list, desc="Getting PubMed Author Data"):
        retries = 0
        while retries <= max_retries:
            try:
                command = f'poetry run python {script_path} -i {pmid}'
                result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
                pubmed_data = json.loads(result)
                if not pubmed_data["authorList"]:
                    print(f"No authorList found for PMID {pmid}")
                else:
                    all_author_data.extend(pubmed_data["authorList"])
                break  # Break out of the retry loop on success
            except subprocess.CalledProcessError as e:
                print(f"Error querying PMID {pmid}: {e}, attempt {retries + 1} of {max_retries}")
                retries += 1
                if retries > max_retries:
                    print(f"Max retries reached for PMID {pmid}. Moving on.")
                else:
                    time.sleep(retry_delay)  # Wait only if we're going to retry

    return all_author_data


# %%
async def fetch_pmid_data(pmid, script_path):
    """
    Asynchronously executes the pubmedAuthorAffiliation.py script for a given PMID
    and returns the parsed JSON data.

    Parameters:
    pmid (str): The PMID for which to fetch author affiliation data.
    script_path (str): The path to the pubmedAuthorAffiliation.py script.

    Returns:
    dict: The JSON data returned by the pubmedAuthorAffiliation.py script.
    """
    command = f'poetry run python {script_path} -i {pmid}'
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        # Process finished successfully, parse JSON output
        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError:
            print(f"Failed to decode JSON output for PMID {pmid}.")
            return None
    else:
        # Process failed, log error
        print(f"Error querying PMID {pmid}: {stderr.decode()}")
        return None


async def query_pubmed_async(pmids_list: list):
    """
    Query PubMed asynchronously for a list of PMIDs and extract "authorList" from each result,
    with a progress bar.
    """
    script_path = "pubmedAuthorAffiliation/pubmedAuthorAffiliation.py"
    all_author_data = []  # This will store all the authorLists

    progress_bar = tqdm(total=len(pmids_list), desc="Processing PMIDs")

    for i in range(0, len(pmids_list), 10):
        batch_pmids = pmids_list[i:i+10]
        tasks = [asyncio.create_task(fetch_pmid_data(pmid, script_path)) for pmid in batch_pmids]
        results = await asyncio.gather(*tasks)
        for result in results:
            if result and "authorList" in result:
                all_author_data.extend(result["authorList"])
            progress_bar.update(1)  # Update progress bar per PMID processed
        await asyncio.sleep(1)  # Respect the rate limit

    progress_bar.close()
    return all_author_data


# %% Running the asynchronous function (in an event loop):
# pmids_list_test = ["37971890", "37630833"]
def extract_pmids(url_list: list):
    pmid_list = []
    pattern = r"https://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/"

    for url in url_list:
        match = re.search(pattern, url)

        if match:
            pmid = match.group(1)
        else:
            pmid = None

        pmid_list.append(pmid)

    return pmid_list


# %%
url_list = 
pmid_list = extract_pmids()

# %%
nest_asyncio.apply()

loop = asyncio.get_event_loop()
if loop.is_running():
    # Run the coroutine in the already running loop
    task = asyncio.ensure_future(query_pubmed_async(pmids_list_test))
    result = loop.run_until_complete(task)
else:
    # If the loop is not running (unlikely in Jupyter), this runs it
    result = loop.run_until_complete(query_pubmed_async(pmids_list_test))

print(result)

# %%
nest_asyncio.apply()

loop = asyncio.get_event_loop()
if loop.is_running():
    # Run the coroutine in the already running loop
    task = asyncio.ensure_future(query_pubmed_async(pmids_list))
    result = loop.run_until_complete(task)
else:
    # If the loop is not running (unlikely in Jupyter), this runs it
    result = loop.run_until_complete(query_pubmed_async(pmids_list))

print(result)

# %%
result_df = pd.DataFrame(result)
result_df.to_pickle('./outputs/addresses_from_names/rneasy_authors.pkl')

# %%
result_df = pd.read_pickle('./outputs/addresses_from_names/rneasy_authors.pkl')
print(result_df)

# %%
filtered_df = result_df[result_df['lastName'].isin(rneasy_df["LastName"])]
# print("RNEASY DF:\n", rneasy_df)
print("FILTERED DF:\n", filtered_df)

# %%
pmids_test = ["37971890", "37630833"]
author_data_test = query_pubmed(pmids_list=pmids_test)
print(author_data_test)

# # %%
# author_data_list = query_pubmed(pmids_list)
# print(author_data_list)

# # %%
# author_data_df = pd.DataFrame(author_data_list)
# author_data_df.to_pickle('./outputs/addresses_from_names/rneasy_authors.pkl')

# # %%
# author_data_df = pd.read_pickle('./outputs/addresses_from_names/rneasy_authors.pkl')
# print("AUTHOR_DATA_DF FROM PICKLE:", author_data_df)
