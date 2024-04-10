import requests
import json

with open('config.json', 'r') as file:
    config = json.load(file)
google_custom_search_api_key = config['apiKeys']['googleCustomSearch']
search_engine_id = config['searchEngineId']


def google_emails(api_key: str, se_id: str, query: str):
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": api_key,
        "cx": se_id,
        "q": query
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        result = response.json()
        print(result)
    else:
        print(f"Failed to retrieve search result: {response.status_code}")


my_query = "Stephan Sommer Viticulture and Enology Research Center , California State University"
google_emails(google_custom_search_api_key, search_engine_id, my_query)
