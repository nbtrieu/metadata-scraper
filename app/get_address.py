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
    result_list = search_result.get("places", [])

    if not result_list:
        return "No results found"

    key_words = set(word.lower() for word in place_name.replace(',', '').split())
    best_match = None

    for result in result_list:
        display_name_field = result["displayName"]["text"]
        address_field = result["formattedAddress"]
        matched_words = sum(word.lower() in display_name_field.lower() for word in key_words)
        match_percentage = matched_words / len(key_words)

        if match_percentage == 1:
            best_match = address_field

        elif match_percentage >= 0.5:
            best_match = address_field

        elif match_percentage < 0.5:
            return result_list[0]["formattedAddress"]

    return best_match


# Test:
# institution_name = 'Department of Microbiology and Immunology, University of Michigan Medical School'  # case: ['displayName']['text'] is 50% match or above
# institution_name = 'Surin Rajabhat University'  # case: multiple result
# institution_name = 'European Molecular Biology Laboratory (EMBL), Structural and Computational Biology Unit, Meyerhofstrasse 1, 69117 Heidelberg, Germany'
search_result = search_place(institution_name, my_api_key)
print('>>> SEARCH RESULT:', search_result)
institution_address = get_address(institution_name)
print('>>> ADDRESS:', institution_address)
