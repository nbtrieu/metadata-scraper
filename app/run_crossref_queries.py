import requests


def get_authors_names(doi_list: list):
    for doi in doi_list:
        url = f"https://api.crossref.org/works/{doi}"

        headers = {
            "User-Agent": "Email nicole.nghi.trieu@gmail.com"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            title = data.get('message', {}).get('title', ['No Title'])[0]
            print("Title:", title)

            authors = data.get('message', {}).get('author', [])
            for author in authors:
                given_name = author.get('given')
                family_name = author.get('family')
                print(f"Author given and family name: {given_name} {family_name}")

            affiliations = author.get('affiliation', [])
            for affiliation in affiliations:
                affiliation_name = affiliation.get('name', 'No Affiliation Name')
                print(f"Affiliation: {affiliation_name}")
        else:
            print(f"Error fetching data: {response.status_code}, {response.text}")


doi_list = ["10.1177/0300985817698207", "10.4049/jimmunol.2000447"]
get_authors_names(doi_list)
