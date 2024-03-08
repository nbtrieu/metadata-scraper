# %%
import requests
import xml.etree.ElementTree as ET
import json
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
        "retmax": 2,  # limit to 2 PMIDs per term
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
print(rneasy_df["FullName"])


# %%
def process_pmids_from_author_names(api_key: str, author_names: list):
    all_pmids = []

    for name in tqdm(author_names, desc="Getting PMIDS"):
        idlist = get_pmids_from_term(api_key, name)
        all_pmids.extend(idlist)

    return all_pmids