import requests
import logging
import json
from tqdm import tqdm

with open('config.json', 'r') as file:
    config = json.load(file)
google_maps_places_api_key = config['apiKeys']['googleMapsPlaces']


def search_place(place, api_key):
    url = 'https://places.googleapis.com/v1/places:searchText'
    payload = {"textQuery": f"address for {place}"}
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f'Connection error occurred: {conn_err}')
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f'Timeout error occurred: {timeout_err}')
    except requests.exceptions.RequestException as req_err:
        logging.error(f'Unexpected error occurred: {req_err}')
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')

    # Return a detailed error message or a structured error object for further processing
    return {"error": True, "status_code": response.status_code if response else 'N/A', "message": response.text if response else 'No response'}


def get_address(place_name):
    search_result = search_place(place_name, google_maps_places_api_key)
    # print('>>> SEARCH RESULT:', search_result)

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

    # print('>>> BEST MATCH ADDRESS:', best_match)
    return best_match


def filter_best_match(result_list: list, place_name: str):
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


def get_address_from_pubmed(publications_list: list, api_key: str):
    all_results = []

    for publication in tqdm(publications_list, desc="Getting Addresses"):
        publication_results = []  # Storing results for each publication separately

        if "authorList" not in publication:
            print(f"Skipping publication {publication.get('pubmedId', 'Unknown')} due to missing 'authorList'")
            continue

        # Extracting 'keyword' and 'pubmedId' from the publication
        keyword = publication.get("keyword", "Unknown")
        pubmedId = publication.get("pubmedId", "Unknown")
        doi = publication.get("doi", "Unknown")

        for author in publication["authorList"]:
            for key in ['affiliation', 'institute']:
                if author.get(key, "") == "Unparsed":  # Skip 'Unparsed' institute values
                    continue

                search_result = search_place(author[key], api_key)

                if search_result == {}:
                    continue  # Skip empty search result
                if search_result.get("error"):
                    print(search_result.get("message"))  # Log the error message
                    continue

                result_list = search_result.get("places", [])
                if not result_list:
                    continue  # Skip this place if no results found

                # Find the best match:
                best_match_address = filter_best_match(result_list, author[key])
                if best_match_address:
                    result_dict = {
                        "keyword": keyword,
                        "pubmed_id": pubmedId,
                        "doi": doi,
                        "author_name": f"{author.get('lastName', '')} {author.get('initials', '')}".strip(),
                        "affiliation": author.get('affiliation', "Unspecified"),
                        "institute": author.get('institute', "Unparsed"),
                        "address": best_match_address
                    }
                    publication_results.append(result_dict)
                    break  # Optionally break if only one address per author is needed

        # Combine all publication results into the main results list
        all_results.extend(publication_results)

    return all_results


def get_address_from_crossref(publications_list: list, api_key: str):
    all_results = []

    for publication in tqdm(publications_list, desc="Getting Addresses"):
        publication_results = []  # Storing results for each publication separately

        if publication.get("authors") == []:
            print(f"Skipping publication {publication.get('doi', 'Unknown')} due to missing 'authors'")
            continue

        # Extracting 'keyword' and 'doi' from the publication
        doi = publication.get("doi", "Unknown")
        keyword = publication.get("keyword", "Unknown")

        for author in publication["authors"]:
            affiliations = author.get("affiliation", [])
            if not affiliations:  # Skip authors with no affiliations
                continue

            # Use only the first affiliation for searching
            first_affiliation = affiliations[0]

            search_result = search_place(first_affiliation, api_key)
            if search_result == {} or search_result.get("error"):
                print(search_result.get("message", "Error during search"))  # Log the error message or a default error message
                continue

            result_list = search_result.get("places", [])
            if not result_list:
                continue  # Skip this place if no results found

            best_match_address = filter_best_match(result_list, first_affiliation)
            if best_match_address:
                result_dict = {
                    "doi": doi,
                    "keyword": keyword,
                    "given_name": author.get('given_name', "Unknown"),
                    "family_name": author.get('family_name', "Unknown"),
                    "affiliation": first_affiliation,  # Store the used affiliation
                    "address": best_match_address
                }
                publication_results.append(result_dict)
                # No break here to allow processing for all authors

        all_results.extend(publication_results)

    return all_results


# Test:
# institution_name = 'University of New England'
# institution_name = 'Surin Rajabhat University'  # case: multiple result
# institution_name = 'European Molecular Biology Laboratory (EMBL), Structural and Computational Biology Unit, Meyerhofstrasse 1, 69117 Heidelberg, Germany'
# search_result = search_place(institution_name, google_maps_places_api_key)
# print('>>> SEARCH RESULT:', search_result)
# institution_address = get_address(institution_name)
# print('>>> BEST MATCH ADDRESS:', institution_address)


# institution_name = "Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA"
# address = get_address(institution_name)
# print(address)

# publications_list = [{'error': False, 'pubmedId': '7275933', 'journalTitle': 'Journal of bacteriology', 'articleTitle': 'Isolation, properties, function, and regulation of endo-(1 leads to 3)-beta-glucanases in Schizosaccharomyces pombe.', 'authorList': [], 'keyword': 'Glucanases'}, {'error': False, 'pubmedId': '37110241', 'journalTitle': 'Microorganisms', 'articleTitle': None, 'authorList': [{'firstName': 'n/a', 'initials': 'SI', 'lastName': 'Codreanu', 'affiliation': 'Faculty of Medicine, "George Emil Palade" University of Medicine, Pharmacy, Sciences and Technology of Târgu Mures, 38 Gheorghe Marinescu Street, 540139 Târgu Mures, Romania.', 'country': 'Romania', 'institute': '"George Emil Palade" University of Medicine'}, {'firstName': 'n/a', 'initials': 'CN', 'lastName': 'Ciurea', 'affiliation': 'Department of Microbiology, Faculty of Medicine, "George Emil Palade" University of Medicine, Pharmacy, Sciences and Technology of Târgu Mures, 38 Gheorghe Marinescu Street, 540139 Târgu Mures, Romania.', 'country': 'Romania', 'institute': '"George Emil Palade" University of Medicine'}], 'keyword': 'Lyticase'}]
# address_list = get_address_bulk(publications_list, google_maps_places_api_key)
# print('ADDRESS LIST:', address_list)

# crossref_data = [{'doi': '10.1177/0300985817698207', 'keyword': 'Lyticase', 'authors': [{'given_name': 'Courtney', 'family_name': 'Meason-Smith', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Erin E.', 'family_name': 'Edwards', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Caitlin E.', 'family_name': 'Older', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Mackenzie', 'family_name': 'Branco', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Laura K.', 'family_name': 'Bryan', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Sara D.', 'family_name': 'Lawhon', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Jan S.', 'family_name': 'Suchodolski', 'affiliation': ['Department of Small Animal Clinical Sciences, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Gabriel', 'family_name': 'Gomez', 'affiliation': ['Texas A&M Veterinary Medical Diagnostic Laboratory, College Station, TX, USA']}, {'given_name': 'Joanne', 'family_name': 'Mansell', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}, {'given_name': 'Aline Rodrigues', 'family_name': 'Hoffmann', 'affiliation': ['Department of Veterinary Pathobiology, College of Veterinary Medicine and Biomedical Sciences, Texas A&M University, College Station, TX, USA']}]}, {'doi': '10.1128/jb.173.10.3101-3108.1991', 'keyword': 'Lyticase', 'authors': [{'given_name': 'J L', 'family_name': 'Patton', 'affiliation': ['Department of Biochemistry, University of Kentucky, Lexington 40536.']}, {'given_name': 'R L', 'family_name': 'Lester', 'affiliation': ['Department of Biochemistry, University of Kentucky, Lexington 40536.']}]}]
# address_list = get_address_from_crossref(crossref_data, google_maps_places_api_key)
# print("ADDRESS LIST:", address_list)
