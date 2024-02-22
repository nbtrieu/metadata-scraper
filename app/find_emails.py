import requests
from typing import Dict

# url = "https://api.hunter.io/v2/email-finder"

# params = {
#     "domain": "mednet.ucla.edu",
#     "first_name": "Joan",
#     "last_name": "Warner",
#     "api_key": "a72ec8033998a514e9dbad54319ed4b52256a907"
# }

# response = requests.get(url, params=params)

# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print(f"Failed to retrieve data: {response.status_code}")


def find_email(domain: str, first_name: str, last_name: str, api_key: str) -> Dict:
    url = "https://api.hunter.io/v2/email-finder"

    params = {
        "domain": domain,
        "first_name": first_name,
        "last_name": last_name,
        "api_key": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        result = response.json()
        print(result)
        email = result["data"]["email"]
        return email

    else:
        print(f"Failed to retrieve data: {response.status_code}")


my_api_key = "a72ec8033998a514e9dbad54319ed4b52256a907"
test_email = find_email("mednet.ucla.edu", "Joan", "Warner", my_api_key)
print(test_email)
