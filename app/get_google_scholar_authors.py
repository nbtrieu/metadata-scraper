# %%
import serpapi
import json
import pickle
import ast
import pandas as pd
from tqdm import tqdm

with open('../config.json', 'r') as file:
    config = json.load(file)
serp_api_key = config['apiKeys']['serp']

client = serpapi.Client(api_key=serp_api_key)

# %%
test_results = client.search({
    'engine': 'google_scholar',
    'q': 'duplex-specific nuclease Evrogen',
    'num': '20',
    'start': 100
})

print(test_results)

# %%
print(len(test_results))

# %%
author_id = test_results["organic_results"][0]["publication_info"]["authors"][0]["author_id"]
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
dsn_results = get_google_scholar_results("duplex-specific nuclease Evrogen")  # list of objects

# %%
print(dsn_results)

# %%
print(len(dsn_results))

# %% Get author_id from Google Scholar API
author_id = dsn_results[1]["organic_results"][1]["publication_info"]["authors"][0]["author_id"]
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
dsn_author_data = get_author_data(dsn_results)

# %%
print(dsn_author_data[0])

# %%
file_path = './outputs/dsn_google/dsn_author_data.pkl'
with open(file_path, 'wb') as file:
    pickle.dump(dsn_author_data, file)

# %%
dsn_df = pd.DataFrame(dsn_author_data)
print(dsn_df)

# %%
file_path = './outputs/dsn_google/dsn_authors.csv'
dsn_df.to_csv(file_path)

# %%
print("Data type of 'interests':", dsn_df['interests'].dtype)
# %%
print("First 10 entries in 'interests':\n", dsn_df['interests'].head(10))

# %% Print raw format of a few entries to see their actual content
for idx, row in dsn_df.head(5).iterrows():
    print(f"Raw entry {idx}: {row['interests']}")

# %%
test_string = "[{'title': 'microbiology', 'link': 'https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:microbiology', 'serpapi_link': 'https://serpapi.com/search.json?engine=google_scholar_profiles&hl=en&mauthors=label%3Amicrobiology'}, {'title': 'veterinary medicine', 'link': 'https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:veterinary_medicine', 'serpapi_link': 'https://serpapi.com/search.json?engine=google_scholar_profiles&hl=en&mauthors=label%3Aveterinary_medicine'}]"

# Try parsing it
try:
    parsed_list = ast.literal_eval(test_string)
    print("Parsed successfully:", parsed_list)
    titles = [d['title'] for d in parsed_list]
    print("Extracted titles:", titles)
except Exception as e:
    print("Error during parsing:", e)

# %%
print(dsn_df['interests'].dtype)
print(dsn_df['interests'].head(10))


# %%
def extract_titles(interests):
    if pd.isna(interests):
        return None  # Handle NaN values directly

    # If the entry is a string, try to convert it to a list
    if isinstance(interests, str):
        try:
            interests = ast.literal_eval(interests)
        except Exception as e:
            print(f"Error converting string to list: {interests[:100]}... Error: {e}")
            return None

    # At this point, interests should be a list
    if not isinstance(interests, list):
        print(f"Unexpected data type after conversion: {type(interests)}")
        return None

    try:
        # Extract 'title' from each dictionary in the list
        titles = [d['title'] for d in interests if 'title' in d]
        return ', '.join(titles)
    except Exception as e:
        print(f"Error processing interests list: {interests[:100]}... Error: {e}")
        return None


# %% Apply the function and print results for the first few rows
dsn_df['interests'] = dsn_df['interests'].apply(extract_titles)

# %%
print(dsn_df.head())

# %%
file_path = './outputs/lyticase_google/processed_lyticase_authors.csv'
dsn_df.to_csv(file_path)

# %%
