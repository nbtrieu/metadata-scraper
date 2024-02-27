import requests


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


my_api_key = "AIzaSyDDoyxDjSolmfvXNswzIEfng15JQzmGNWc"
my_se_id = "e7ecd2aa0903946a1"
my_query = "Stephan Sommer Viticulture and Enology Research Center , California State University"
google_emails(my_api_key, my_se_id, my_query)
