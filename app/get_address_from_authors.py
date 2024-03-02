import requests
import json

with open('config.json', 'r') as file:
    config = json.load(file)
google_maps_places_api_key = config['apiKeys']['googleMapsPlaces']


def search_place_from_authors(author, api_key):
    api_key = google_maps_places_api_key

    url = 'https://places.googleapis.com/v1/places:searchText'

    payload = {
        "textQuery": f"address for affiliated institution of {author}"
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel'
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code}, {response.text}"


# def filter_address(place_name):
#     search_result = search_place_from_authors(place_name, google_maps_places_api_key)
#     result_list = search_result["places"]
#     for result in result_list:
#         display_name_field = result["displayName"]["text"]
#         address_field = result["formattedAddress"]
#         if (display_name_field == place_name):
#             return address_field
#         else:
#             continue


# Test:
author_name = 'Joseph Stephen Glavy'
institution_address = search_place_from_authors(author_name, google_maps_places_api_key)
print(institution_address)
