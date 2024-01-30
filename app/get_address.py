import requests

my_api_key = 'AIzaSyBeVCa6qSE3QnzaVN4QvVIZWGNAjpvHTGk'


def search_place(place, api_key):
    api_key = my_api_key

    url = 'https://places.googleapis.com/v1/places:searchText'

    payload = {
        "textQuery": f"address for {place}"
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


def get_address(place_name):
    search_result = search_place(place_name, my_api_key)
    result_list = search_result["places"]

    key_words = place_name.replace(',', '').split()
    key_words = set(key.lower() for key in key_words)

    for result in result_list:
        display_name_field = result["displayName"]["text"]
        address_field = result["formattedAddress"]
        matched_words = sum(
            word.lower() in display_name_field.lower() for word in key_words
        )

        if matched_words >= len(key_words) / 2:
            return address_field

    return None


# FOR LATER: we can use Google Maps Address Validation API to validate address

# Test:
# institution_name = 'Department of Microbiology and Immunology, University of Michigan Medical School'
institution_name = 'Qingdao Institute of Bioenergy and Bioprocess Technology'
search_result = search_place(institution_name, my_api_key)
print('>>> SEARCH RESULT:', search_result)
institution_address = get_address(institution_name)
print('>>> ADDRESS:', institution_address)
