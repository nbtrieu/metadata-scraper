import requests
import pandas as pd
from typing import Dict
from tqdm import tqdm
from extract_params import *


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


def find_email_bulk(params_list: list) -> pd.DataFrame:
    all_results = []
    url = "https://api.hunter.io/v2/email-finder"

    for params in tqdm(params_list, desc="Hunting Emails"):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            print(result)
            result_dict = {
                "first_name": params.get("first_name"),
                "last_name": params.get("last_name"),
                "email": result["data"]["email"]
            }
            all_results.append(result_dict)

        else:
            print(f"Failed to retrieve data for {params.get('first_name')} {params.get('last_name')}: {response.status_code}")

    email_df = pd.DataFrame(all_results)
    email_df.to_csv(
        'ucla_emails_hunter.csv',
        sep=',',
        columns=['first_name', 'last_name', 'email'],
        header=True,
        index=False,
        encoding='utf-8'
    )

    return email_df


my_api_key = "a72ec8033998a514e9dbad54319ed4b52256a907"

# ucla_email_df = pd.read_csv("data/ucla_contacts.csv")
# params_list = create_params_list(ucla_email_df, my_api_key)
# params_list = [
#     {'domain': 'mednet.ucla.edu', 'first_name': 'Rita', 'last_name': 'Simon', 'api_key': 'a72ec8033998a514e9dbad54319ed4b52256a907'},
#     {'domain': 'mednet.ucla.edu', 'first_name': 'Ivan', 'last_name': 'Cortes', 'api_key': 'a72ec8033998a514e9dbad54319ed4b52256a907'},
#     {'domain': 'mednet.ucla.edu', 'first_name': 'Grace', 'last_name': 'Nicassio', 'api_key': 'a72ec8033998a514e9dbad54319ed4b52256a907'}
# ]
# hunter_email_df = find_email_bulk(params_list)
# print(hunter_email_df)

test_email = find_email("mednet.ucla.edu", "Jennifer", "Lowe", my_api_key)
print(test_email)
