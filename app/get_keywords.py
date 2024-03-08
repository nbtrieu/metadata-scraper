# %%
import requests
import json
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

with open('../config.json', 'r') as file:
    config = json.load(file)
ncbi_api_key = config['apiKeys']['ncbi']


# def get_pmids_from_term(api_key: str, term: str):
#     url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

#     params = {
#         "db": "pubmed",
#         "term": term,
#         "retmode": "json",
#         "api_key": api_key
#     }

#     response = requests.get(url=url, params=params)

#     if response.status_code == 200:
#         data = response.json()  # get specifically the 'idlist' field value

#         if 'esearchresult' in data and 'idlist' in data['esearchresult']:
#             idlist = data['esearchresult']['idlist']
#         else:
#             print(f"The expected 'idlist' for {term} was not found in the response.")
#             return []

#         if not idlist:
#             print(f"No PMIDs found for term: {term}")
#             return []
#         else:
#             pmids = ','.join(idlist)
#             return pmids

#     else:
#         print(f"Failed to retrieve search result: {response.status_code}")


# %%
def get_pmids_from_term(api_key: str, term: str):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "api_key": api_key
    }

    # Create a session object
    session = requests.Session()

    # Define retry strategy
    retries = Retry(total=5,  # Total number of retries to allow
                    backoff_factor=1,  # A backoff factor to apply between attempts
                    status_forcelist=[500, 502, 503, 504],  # A set of HTTP status codes that we should force a retry on
                    method_whitelist=["GET"])  # Enable retries for GET method

    # Mount it to the session
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        # Ensure we respect the rate limit by sleeping 1 second / 10 requests
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
                pmids = ','.join(idlist)
                return pmids
        else:
            print(f"Failed to retrieve search result: {response.status_code}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []


def get_keywords_from_pmids(api_key: str, pmids: str):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": pmids,
        "retmode": "xml",
        "api_key": api_key
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        all_results = []
        # Parse the XML response
        root = ET.fromstring(response.text)
        for article in root.findall('.//PubmedArticle'):
            pmid = article.find('.//PMID').text
            keywords_list = article.find('.//KeywordList')
            keywords = []
            if keywords_list is not None:
                for keyword in keywords_list:
                    keywords.append(keyword.text)
            # Skip the article if the keywords list is empty
            if not keywords:
                print("Skipping this article due to empy KeywordList")
                continue
            result_dict = {
                "pmid": pmid,
                "keywords": keywords
            }
            all_results.append(result_dict)

        return all_results

    else:
        print(f"Failed to retrieve search result: {response.status_code}")


def get_keywords_from_author_names(api_key: str, author_name_list: list):
    all_results = []

    for author_name in tqdm(author_name_list, desc="Getting keywords"):
        pmids = get_pmids_from_term(api_key, author_name)
        if pmids:
            keyword_lists = get_keywords_from_pmids(api_key, pmids)
            for keyword_list in keyword_lists:
                keyword_list["author_name"] = author_name
                # print(keyword_list)

            all_results.extend(keyword_lists)

        else:
            # print(f"Skipping author '{author_name}' due to no PMIDs found.")
            continue

    return all_results


# %%
# author_name = "RNeasy 96 Kit"
# pmids = get_pmids_from_term(ncbi_api_key, author_name)
# print(pmids)
# # pmids = "28346123,26542075"
# keywords = get_keywords_from_pmids(ncbi_api_key, pmids)
# print(keywords)

# leads_name_list = ["Juan Roman", "Nataliya Bulayeva"]
# all_keywords = get_keywords_from_author_names(ncbi_api_key, author_name_list)
# print(all_keywords)

leads_df = pd.read_csv("data/split_tables/split_1.csv")
leads_name_list = leads_df["Full Name"].tolist()
leads_keywords_list = get_keywords_from_author_names(ncbi_api_key, leads_name_list)
# print(leads_keywords_list)
leads_keywords_df = pd.DataFrame(leads_keywords_list)
leads_keywords_df.to_pickle('./outputs/leads_keywords_1.pkl')

# %%
leads_keywords_df = pd.read_pickle('./outputs/leads_keywords_1.pkl')
print("FROM PICKLE:\n", leads_keywords_df)
leads_keywords_df['keywords'] = leads_keywords_df['keywords'].apply(
    lambda x: ', '.join([str(k).lower().capitalize() for k in x if k is not None])
)
print("POST LAMBDA:\n", leads_keywords_df)
filename = './outputs/leads_keywords_1.csv'
leads_keywords_df.to_csv(filename, index=False)
