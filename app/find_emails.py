import requests

url = "https://api.hunter.io/v2/email-finder"

params = {
    "domain": "chem.ucla.edu",
    "first_name": "Daniel",
    "last_name": "Jacobs",
    "api_key": "a72ec8033998a514e9dbad54319ed4b52256a907"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Failed to retrieve data: {response.status_code}")
