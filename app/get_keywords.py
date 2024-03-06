import requests
import json
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm

with open('../config.json', 'r') as file:
    config = json.load(file)
ncbi_api_key = config['apiKeys']['ncbi']


def get_pmids_from_term(api_key: str, term: str):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "api_key": api_key
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        data = response.json()  # get specifically the 'idlist' field value

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
            # print(f"PMID: {pmid}, Keywords: {', '.join(keywords)}")
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
            for keyword_list in tqdm(keyword_lists, desc="Processing keywords"):
                keyword_list["author_name"] = author_name
                # print(keyword_list)

            all_results.extend(keyword_lists)

        else:
            print(f"Skipping author '{author_name}' due to no PMIDs found.")
            continue  # Skip this author and continue with the next one

    return all_results


# author_name = "RNeasy 96 Kit"
# pmids = get_pmids_from_term(ncbi_api_key, author_name)
# print(pmids)
# # pmids = "28346123,26542075"
# keywords = get_keywords_from_pmids(ncbi_api_key, pmids)
# print(keywords)

# author_name_list = ["Philip Bennallack", "Anne Keller-Novak"]
# all_keywords = get_keywords_from_author_names(ncbi_api_key, author_name_list)
# print(all_keywords)

leads_df = pd.read_csv("data/2019-2023_Leads_List_Test_deduped.csv")
leads_name_list = leads_df["Full Name"].tolist()
leads_keywords_list = get_keywords_from_author_names(ncbi_api_key, leads_name_list)
# print(leads_keywords_list)
leads_keywords_df = pd.DataFrame(leads_keywords_list)
# print(leads_keywords_df)
leads_keywords_df['keywords'] = leads_keywords_df['keywords'].apply(lambda x: ', '.join(x))
filename = './outputs/leads_keywords.csv'
leads_keywords_df.to_csv(filename, index=False)
