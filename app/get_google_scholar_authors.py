# %%
import serpapi
import json
import pandas as pd
from tqdm import tqdm

with open('../config.json', 'r') as file:
    config = json.load(file)
serp_api_key = config['apiKeys']['serp']

client = serpapi.Client(api_key=serp_api_key)

# %%
results = client.search({
    'engine': 'google_scholar',
    'q': 'Lyticase',
})

# print(type(results))

# %% Get author_id from Google Scholar API
author_id = results["organic_results"][1]["publication_info"]["authors"][0]["author_id"]
# publication_info = results["organic_results"][1]["publication_info"]
print(author_id)

# %% Get affliations from Google Scholar Author SerpApi
author_results = client.search({
    "engine": "google_scholar_author",
    "author_id": author_id,
})

# %%
author_affiliations = author_results["author"]
print(author_affiliations)


# %%
def get_author_data(google_scholar_results):
    all_data = []

    for result in tqdm(
        google_scholar_results["organic_results"],
        desc="Extracting author IDs"
    ):
        if result["publication_info"]["authors"]:
            for author in result["publication_info"]["authors"]:
                author_id = author["author_id"]
                author_results = client.search({
                    "engine": "google_scholar_author",
                    "author_id": author_id,
                })
                author_data = author_results["author"]
                all_data.append(author_data)

    return all_data


# %%
lyticase_author_data = get_author_data(results)
