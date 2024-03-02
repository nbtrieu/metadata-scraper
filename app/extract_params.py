import pandas as pd
import json
from typing import List
from tqdm import tqdm

with open('config.json', 'r') as file:
    config = json.load(file)
hunter_api_key = config['apiKeys']['hunter']


def get_domain(email: str) -> str:
    return email.split("@")[1].lower()


def get_last_name(name: str) -> str:
    return name.split()[-1].lower().capitalize()


def get_first_name(name: str) -> str:
    return name.split()[0].lower().capitalize()


def create_params_list(email_df: pd.DataFrame, api_key: str) -> List:
    params_list = []

    for _, row in tqdm(
        email_df.iterrows(),
        total=email_df.shape[0],
        desc="Extracting Params"
    ):
        params = {
            "domain": get_domain(row["Email"]),
            "first_name": get_first_name(row["Name"]),
            "last_name": get_last_name(row["Name"]),
            "api_key": api_key
        }

        params_list.append(params)

    return params_list


# ucla_email_df = pd.read_csv("data/ucla_contacts.csv")
# # print(ucla_email_df)
# ucla_params = create_params_list(ucla_email_df, hunter_api_key)
# if ucla_params:
#     for param in ucla_params[-3:]:
#         print(param)

# example_email = "RISIMON@MEDNET.UCLA.EDU"
# test_domain = get_domain(example_email)
# print(test_domain)

# example_name = "Susanne de la NICHTERWITZ"
# test_first_name = get_first_name(example_name)
# test_last_name = get_last_name(example_name)
# print(test_first_name)
# print(test_last_name)
