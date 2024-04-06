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
def get_google_scholar_results(keyword: str):
    all_results = []

    for i in tqdm(range(0, 500, 20), desc="Getting Google Scholar results"):
        results = client.search({
            'engine': 'google_scholar',
            'q': keyword,
            'num': '20',
            'start': i
        })
        all_results.extend(results)


# %%
lyticase_results = get_google_scholar_results("lyticase")

# %%
print(lyticase_results)

# %% Get author_id from Google Scholar API
author_id = lyticase_results["organic_results"][1]["publication_info"]["authors"][0]["author_id"]
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

    for result in tqdm(google_scholar_results.get("organic_results", []),
                       desc="Extracting author data"):
        # Check if 'authors' key exists in 'publication_info' before proceeding
        if "authors" in result.get("publication_info", {}):
            for author in result["publication_info"]["authors"]:
                try:
                    author_id = author.get("author_id")
                    # Proceed only if author_id is found
                    if author_id:
                        author_results = client.search({
                            "engine": "google_scholar_author",
                            "author_id": author_id,
                        })
                        # Directly append 'author' data assuming it's always present
                        author_data = author_results["author"]
                        all_data.append(author_data)
                except Exception as e:
                    print(f"Error retrieving data for author ID {author_id}: {e}")
                    # Skip to the next author if an error occurs
                    continue

    return all_data


# %%
lyticase_author_data = get_author_data(lyticase_results)

# %%
lyticase_df = pd.DataFrame(lyticase_author_data).drop_duplicates()
print(lyticase_df)

# %%
file_path = './outputs/lyticase_google/lyticase_authors.csv'
lyticase_df.to_csv(file_path)

# %%
