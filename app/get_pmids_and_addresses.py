# %%
import requests
import xml.etree.ElementTree as ET
import json
import subprocess
import time
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

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
    values (list): A list of PMID strings

    Returns:
    list: A list of dictionaries.
    """

    script_path = "pubmedAuthorAffiliation/pubmedAuthorAffiliation.py"
    all_author_data = []

    for pmid in tqdm(pmids_list, desc="Querying PubMed"):
        command = f'poetry run python {script_path} -i {pmid}'
        result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
        # print("Attempting to parse JSON:", result[:500])
        pubmed_data = json.loads(result)

        for author_data in pubmed_data["authorList"]:
            all_author_data.append(author_data)

    return all_author_data


# %%
pmids_test = ["37971890", "37630833"]
author_data_test = query_pubmed(pmids_list=pmids_test)
print(author_data_test)

# %%
