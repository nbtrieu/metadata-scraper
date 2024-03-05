import requests
import json
import xml.etree.ElementTree as ET

with open('../config.json', 'r') as file:
    config = json.load(file)
ncbi_api_key = config['apiKeys']['ncbi']


def get_pmids_from_author(api_key: str, author_name: str):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": author_name,
        "retmode": "json",
        "api_key": api_key
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        data = response.json()  # get specifically the 'idlist' field value
        idlist = data['esearchresult']['idlist']
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


def get_keywords_from_authors()


author_name = "Courtney Meason-Smith"
pmids = get_pmids_from_author(ncbi_api_key, author_name)
print(pmids)
# pmids = "28346123,26542075"
keywords = get_keywords_from_pmids(ncbi_api_key, pmids)
print(keywords)
