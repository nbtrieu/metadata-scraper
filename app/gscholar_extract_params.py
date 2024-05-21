# %%
import pandas as pd
import json
import pickle
from typing import List
from tqdm import tqdm

with open('../config.json', 'r') as file:
    config = json.load(file)
hunter_api_key = config['apiKeys']['hunter']


# %%
def get_domain(email: str) -> str:
    return email.split(" at ")[1].lower()


def get_last_name(name: str) -> str:
    return name.split()[-1].lower().capitalize()


def get_first_name(name: str) -> str:
    return name.split()[0].lower().capitalize()


def create_params_list(authors_df: pd.DataFrame, api_key: str) -> List:
    params_list = []

    for _, row in tqdm(
        authors_df.iterrows(),
        total=authors_df.shape[0],
        desc="Extracting Params"
    ):
        if pd.notna(row['name']) and pd.notna(row['email']):
            params = {
                "domain": get_domain(row["email"]),
                "first_name": get_first_name(row["name"]),
                "last_name": get_last_name(row["name"]),
                "api_key": api_key
            }

            params_list.append(params)

    return params_list


# %%
# gscholar_dsn_df = pd.read_csv("./outputs/dsn_google/dsn_authors.csv", nrows=10)
gscholar_dsn_df = pd.read_csv("./outputs/dsn_google/dsn_authors.csv")
# print(ucla_email_df)
gscholar_dsn_params = create_params_list(gscholar_dsn_df, hunter_api_key)
if gscholar_dsn_params:
    for param in gscholar_dsn_params[-3:]:
        print(param)

# %%
file_path = './outputs/dsn_google/dsn_params_list.pkl'
with open(file_path, 'wb') as file:
    pickle.dump(gscholar_dsn_params, file)

# %%
#  example_email = "RISIMON@MEDNET.UCLA.EDU"
# test_domain = get_domain(example_email)
# print(test_domain)

# example_name = "Susanne de la NICHTERWITZ"
# test_first_name = get_first_name(example_name)
# test_last_name = get_last_name(example_name)
# print(test_first_name)
# print(test_last_name)
