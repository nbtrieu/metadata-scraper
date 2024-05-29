# %%
import asyncio
import nest_asyncio
# import aiohttp
import logging
import json
# from tqdm.asyncio import tqdm
import pandas as pd
from tqdm import tqdm
from get_address import search_place, filter_best_match

# %%
with open('../config.json', 'r') as file:
    config = json.load(file)
google_maps_places_api_key = config['apiKeys']['googleMapsPlaces']


# %%
def get_initials(row):
    initials = ""
    if pd.notnull(row['firstName']) and isinstance(row['firstName'], str):
        initials = row['firstName'][0]
        if 'MiddleName' in row and pd.notnull(row['MiddleName']):
            middle_names = row['MiddleName'].split()
            for name in middle_names:
                initials += name[0]
    return initials

def process_author_dicts(
    pubmed_result_file_path,
    lead_source_file_path,
    leadsource_lastname_column_name,
    leadsource_firstname_column_name
):
    pubmed_result_df = pd.read_pickle(pubmed_result_file_path)
    # drop 'firstName' column because all n/a values
    pubmed_result_df.drop(columns=['firstName'], inplace=True)
    print("PUBMED RESULT DF:\n", pubmed_result_df)

    lead_source_df = pd.read_csv(lead_source_file_path).rename(
        columns={
            leadsource_lastname_column_name: 'lastName',
            leadsource_firstname_column_name: 'firstName'
        }
    )
    lead_source_df['initials'] = lead_source_df.apply(get_initials, axis=1)
    print("LEAD DF WITH INITIALS:\n", lead_source_df)
    merged_df = pd.merge(pubmed_result_df, lead_source_df, on=['lastName', 'initials'], how='inner')
    print("MERGED DF: \n", merged_df)
    filtered_df = merged_df[['firstName', 'initials', 'lastName', 'affiliation', 'institute']]
    print("FILTERED DF:\n", filtered_df)
    deduped_filtered_df = filtered_df.drop_duplicates().reset_index(drop=True)
    deduped_filtered_df.to_csv('./outputs/test_deduped_filtered.csv', index=False)
    author_dicts = deduped_filtered_df.to_dict('records')
    print("length of author_dicts:", len(author_dicts))

    return author_dicts


# %%
def get_address_from_author_dicts(author_dicts: list, api_key: str):
    all_results = []

    for author_dict in tqdm(author_dicts, desc="Getting Addresses"):
        for key in ['affiliation', 'institute']:
            if author_dict.get(key, "") == "Unparsed":  # Skip 'Unparsed' values
                continue

            search_result = search_place(author_dict[key], api_key)

            if search_result == {}:
                continue  # Skip empty search result
            if search_result.get("error"):
                print(search_result.get("message"))  # Log the error message
                continue

            result_list = search_result.get("places", [])
            if not result_list:
                continue  # Skip if no results found

            # Find the best match:
            best_match_address = filter_best_match(result_list, author_dict[key])
            if best_match_address:
                result_dict = {
                    "firstName": author_dict.get('firstName'),
                    "initials": author_dict.get('initials'),
                    "lastName": author_dict.get('lastName'),
                    "pubmed_affiliation": author_dict.get('affiliation', "Unspecified"),
                    "pubmed_institute": author_dict.get('institute', "Unparsed"),
                    "address": best_match_address
                }
                all_results.append(result_dict)
                break  # Assuming you only want one address per author

    return all_results


# %%
def process_addresses(address_dicts: dict, lead_source_file_path: str, output_filename: str):
    address_df = pd.DataFrame(address_dicts)
    print("ADDRESS DF:\n", address_df)
    deduped_address_df = address_df.drop_duplicates()
    print("DEDUPED ADDRESS DF:\n", deduped_address_df)
    leadsource_df = pd.read_csv(lead_source_file_path)
    leadsource_df.rename(columns={'LastName': 'lastName', 'FirstName': 'firstName'}, inplace=True)
    print("LEADSOURCE DF:\n", leadsource_df)
    matching_df = pd.merge(leadsource_df, deduped_address_df, on=['firstName', 'lastName'], how='left').drop_duplicates().reset_index(drop=True)
    print("MATCHING DF:\n", matching_df)
    matching_df.to_csv(output_filename, index=False)


# %%
author_dicts = process_author_dicts(
    pubmed_result_file_path='./outputs/rabbit/rabbit_authors_4_2.pkl',
    lead_source_file_path='./data/rabbit/smaller_csv_file_4.csv',
    leadsource_lastname_column_name='LastName',
    leadsource_firstname_column_name='FirstName'
)

print(len(author_dicts))

# %%
address_dicts = get_address_from_author_dicts(author_dicts, google_maps_places_api_key)

# %%
process_addresses(
    address_dicts=address_dicts,
    lead_source_file_path='./data/rabbit/smaller_csv_file_4.csv',
    output_filename='./outputs/rabbit/addresses/matched_rabbit_addresses_4_2.csv'
)
