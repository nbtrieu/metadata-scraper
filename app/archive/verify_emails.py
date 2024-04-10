import requests

url = "https://api.hunter.io/v2/email-verifier"

params = {
    "email": "hmamsa@ucla.edu",
    "api_key": "a72ec8033998a514e9dbad54319ed4b52256a907"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Failed to verify email: {response.status_code}")
