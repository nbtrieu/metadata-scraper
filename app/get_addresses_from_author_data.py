# %%
import asyncio
import nest_asyncio
import aiohttp
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
    author_dicts = deduped_filtered_df.to_dict('records')
    print("length of author_dicts:", len(author_dicts))

    return author_dicts

# %%
author_dicts = process_author_dicts(
    pubmed_result_file_path='./outputs/rabbit/rabbit_authors_2_1.pkl',
    lead_source_file_path='./data/rabbit/smaller_csv_file_2.csv',
    leadsource_lastname_column_name='LastName',
    leadsource_firstname_column_name='FirstName'
)

print(len(author_dicts))



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
address_dicts = get_address_from_author_dicts(author_dicts, google_maps_places_api_key)


# %%
def process_addresses(address_dicts: dict, lead_source_file_path: str, output_filename: str):
    address_df = pd.DataFrame(address_dicts)
    print("ADDRESS DF:\n", address_df)
    address_df.to_pickle('./outputs/cold/coral_addresses.pkl')
    deduped_address_df = address_df.drop_duplicates()
    print("DEDUPED ADDRESS DF:\n", deduped_address_df)
    leadsource_df = pd.read_csv(lead_source_file_path)
    leadsource_df.rename(columns={'LastName': 'lastName', 'FirstName': 'firstName'}, inplace=True)
    print("LEADSOURCE DF:\n", leadsource_df)
    matching_df = pd.merge(leadsource_df, deduped_address_df, on=['firstName', 'lastName'], how='left').drop_duplicates().reset_index(drop=True)
    print("MATCHING DF:\n", matching_df)
    matching_df.to_csv(output_filename, index=False)


# %%
process_addresses(
    address_dicts=address_dicts,
    lead_source_file_path='./data/rabbit/smaller_csv_file_2.csv',
    output_filename='./outputs/rabbit/addresses/matched_rabbit_addresses_2_2.csv'
)


# %%
def get_address_from_google_scholar_authors(author_dicts: list, api_key: str):
    all_results = []

    for author_dict in tqdm(author_dicts, desc="Getting Addresses"):
        if author_dict.get('affiliations', "") == "Unparsed":  # Skip 'Unparsed' values
            continue

        search_result = search_place(author_dict['affiliations'], api_key)

        if search_result == {}:
            continue  # Skip empty search result
        if search_result.get("error"):
            print(search_result.get("message"))  # Log the error message
            continue

        result_list = search_result.get("places", [])
        if not result_list:
            continue  # Skip if no results found

        # Find the best match:
        best_match_address = filter_best_match(result_list, author_dict['affiliations'])
        if best_match_address:
            result_dict = {
                "name": author_dict.get('name'),
                "gscholar_affiliation": author_dict.get('affiliations', "Unspecified"),
                "interests": author_dict.get('interests', "N/A"),
                "address": best_match_address
            }
            all_results.append(result_dict)

    return all_results


# %%
lyticase_author_df = pd.read_csv('./outputs/lyticase_google/processed_lyticase_authors.csv').drop_duplicates()
print(lyticase_author_df)

# %%
lyticase_author_dicts = lyticase_author_df.to_dict('records')
print(len(lyticase_author_dicts))

# %%
lyticase_addresses = get_address_from_google_scholar_authors(lyticase_author_dicts, google_maps_places_api_key)

# %%
lyticase_address_df = pd.DataFrame(lyticase_addresses)
print("ADDRESS DF:\n", lyticase_address_df)

# %%
lyticase_address_df.to_pickle('./outputs/lyticase_google/lyticase_gscholar_addresses.pkl')
deduped_lyticase_address_df = lyticase_address_df.drop_duplicates()
print("DEDUPED ADDRESS DF:\n", deduped_lyticase_address_df)
deduped_lyticase_address_df.to_csv('./outputs/lyticase_google/lyticase_gscholar_addresses.csv', index=False)

# %%
# async def search_place_async(place, api_key):
#     url = 'https://places.googleapis.com/v1/places:searchText'
#     payload = {"textQuery": f"address for {place}"}
#     headers = {
#         'Content-Type': 'application/json',
#         'X-Goog-Api-Key': api_key,
#         'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel'
#     }

#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.post(url, json=payload, headers=headers) as response:
#                 if response.status == 200:
#                     return await response.json()
#                 else:
#                     return {"error": True, "status_code": response.status, "message": await response.text}

#         except aiohttp.ClientError as e:
#             logging.error(f'HTTP client error occurred: {e}')
#             return {"error": True, "message": f'HTTP client error occurred: {e}'}
#         except asyncio.TimeoutError as e:
#             logging.error(f'Timeout error occurred: {e}')
#             return {"error": True, "message": f'Timeout error occurred: {e}'}
#         except Exception as e:
#             logging.error(f'An unexpected error occurred: {e}')
#             return {"error": True, "message": f'An unexpected error occurred: {e}'}


# # %%
# async def get_address_from_author_dicts_async(author_dicts: list, api_key: str):
#     all_results = []

#     async def process_author_dict(author_dict):
#         for key in ['affiliation', 'institute']:
#             if author_dict.get(key, "") == "Unparsed":
#                 continue

#             search_result = await search_place_async(author_dict[key], api_key)

#             if search_result == {}:
#                 continue
#             if search_result.get("error"):
#                 print(search_result.get("message"))
#                 continue

#             result_list = search_result.get("places", [])
#             if not result_list:
#                 continue

#             best_match_address = filter_best_match(result_list, author_dict[key])  # Assuming this is a synchronous function
#             if best_match_address:
#                 return {
#                     "intials": author_dict.get('initials'),
#                     "lastName": author_dict.get('lastName'),
#                     "affiliation": author_dict.get('affiliation', "Unspecified"),
#                     "institute": author_dict.get('institute', "Unparsed"),
#                     "address": best_match_address
#                 }

#     tasks = [process_author_dict(author_dict) for author_dict in author_dicts]
#     for i in tqdm(range(0, len(tasks), 10), desc="Getting Addresses"):
#         batch = tasks[i:i+10]
#         results = await asyncio.gather(*batch)
#         # Filter out None results and extend all_results
#         all_results.extend([result for result in results if result])
#         await asyncio.sleep(1)  # Sleep to respect the rate limit of 10 req/s

#     return all_results


# # %%
# nest_asyncio.apply()

# loop = asyncio.get_event_loop()
# if loop.is_running():
#     task = asyncio.ensure_future(get_address_from_author_dicts_async(
#             author_dicts, google_maps_places_api_key
#         ))
#     address_dicts = loop.run_until_complete(task)
# else:
#     address_dicts = loop.run_until_complete(
#         get_address_from_author_dicts_async(
#             author_dicts, google_maps_places_api_key
#         )
#     )
