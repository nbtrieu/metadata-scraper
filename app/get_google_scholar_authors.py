# %%
import serpapi
import json
import pickle
import pandas as pd
from tqdm import tqdm

with open('../config.json', 'r') as file:
    config = json.load(file)
serp_api_key = config['apiKeys']['serp']

client = serpapi.Client(api_key=serp_api_key)

# %%
test_results = client.search({
    'engine': 'google_scholar',
    'q': 'lyticase',
    'num': '20',
    'start': 100
})

print(test_results)

# %%
print(len(test_results))

# %%
author_id = test_results["organic_results"][5]["publication_info"]["authors"][0]["author_id"]
# publication_info = results["organic_results"][1]["publication_info"]
print(author_id)


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
        all_results.append(results)

    return all_results


# %%
lyticase_results = get_google_scholar_results("lyticase")  # list of objects

# %%
print(lyticase_results)

# %%
print(len(lyticase_results))

# %% Get author_id from Google Scholar API
author_id = lyticase_results[0]["organic_results"][1]["publication_info"]["authors"][0]["author_id"]
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

    for result in tqdm(google_scholar_results, desc="Extracting author data"):
        # Check if 'publication_info' is in result and 'authors' key exists in 'publication_info' before proceeding
        organic_results = result.get("organic_results", {})
        for organic_result in organic_results:
            publication_info = organic_result.get("publication_info", {})
            if "authors" in publication_info:
                for author in publication_info["authors"]:
                    try:
                        author_id = author.get("author_id")
                        # Proceed only if author_id is found
                        if author_id:
                            author_results = client.search({
                                "engine": "google_scholar_author",
                                "author_id": author_id,
                            })
                            # Directly append 'author' data assuming it's always present
                            author_data = author_results.get("author", {})
                            if author_data:
                                all_data.append(author_data)
                    except Exception as e:
                        print(f"Error retrieving data for author ID {author_id}: {e}")
                        # Skip to the next author if an error occurs
                        continue

    return all_data


# %%
lyticase_author_data = get_author_data(lyticase_results)

# %%
print(lyticase_author_data[0])

# %%
file_path = './outputs/lyticase_google/lyticase_author_data.pkl'
with open(file_path, 'wb') as file:
    pickle.dump(lyticase_author_data, file)

# %%
lyticase_df = pd.DataFrame(lyticase_author_data)
print(lyticase_df)

# %%
# lyticase_df = lyticase_df.drop_duplicates()
# print(lyticase_df)

# %%
file_path = './outputs/lyticase_google/lyticase_authors.csv'
lyticase_df.to_csv(file_path)

# %%
