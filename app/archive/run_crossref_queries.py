import requests
import pandas as pd
from tqdm import tqdm


def query_crossref(doi_list: list, papers_df: pd.DataFrame):
    all_results = []

    for doi in tqdm(doi_list, desc="Querying Crossref"):
        url = f"https://api.crossref.org/works/{doi}"
        headers = {"User-Agent": "Email nicole.nghi.trieu@gmail.com"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result_dict = response.json()['message']

            # Retrieve keyword from papers_df
            paper_info = papers_df.loc[papers_df['doi'] == doi]
            if not paper_info.empty:
                keyword = paper_info.iloc[0]['keyword']
            else:
                keyword = 'Keyword Not Found'

            authors_list = result_dict.get('author', [])
            authors_with_affiliations = []

            # Iterate through each author to capture their given name, family name, and affiliation
            for author in authors_list:
                author_dict = {
                    'given_name': author.get('given', "Unknown"),
                    'family_name': author.get('family', "Unknown"),
                    'affiliation': [aff.get('name', 'No Affiliation Name') for aff in author.get('affiliation', [])]
                }
                authors_with_affiliations.append(author_dict)

            # Compile all relevant information into a result dictionary for this DOI
            publication_result = {
                'doi': doi,
                'keyword': keyword,
                'authors': authors_with_affiliations
            }

            all_results.append(publication_result)
        else:
            print(f"Error fetching data for DOI {doi}: {response.status_code}, {response.text}")

    return all_results


def format_author_name(given_name, family_name):
    # Replace periods to handle middle initials correctly and then extract initials
    initials = "".join([name[0] for name in given_name.replace('.', ' ').split() if name]).upper()
    # Concatenate initials with the family name
    formatted_name = f"{family_name} {initials}"
    # print("FORMATTED NAME:", formatted_name)
    return formatted_name


def get_authors_name(doi_list: list):
    authors_names = []

    for doi in tqdm(doi_list, desc="Querying Crossref"):
        url = f"https://api.crossref.org/works/{doi}"
        headers = {"User-Agent": "Email example@example.com"}  # Change to your actual email
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result_dict = response.json()['message']
            authors_list = result_dict.get('author', [])
            for author in authors_list:
                given_name = author.get('given', "")
                family_name = author.get('family', "")
                formatted_author_name = format_author_name(given_name, family_name)
                author_dict = {
                    'doi': doi,
                    'author_name': formatted_author_name,  # This will be used for matching
                    'given_name': given_name,
                    'family_name': family_name,
                }
                authors_names.append(author_dict)

        else:
            print(f"Error fetching data for DOI {doi}: {response.status_code}, {response.text}")

    authors_names_df = pd.DataFrame(authors_names)
    authors_names_df.to_csv(
        'authors_names_list.csv',
        sep=',',
        columns=['doi', 'author_name', 'given_name', 'family_name'],
        header=True,
        index=False,
        encoding='utf-8'
    )

    return authors_names_df


def create_authors_address_table():
    pubmed_address_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/pubmed_address_list.csv', dtype={'doi': str})
    doi_list = pubmed_address_df['doi'].tolist()
    authors_names_df = get_authors_name(doi_list)

    # Merge using both 'doi' and 'author_name' for a precise match
    merged_df = pd.merge(authors_names_df, pubmed_address_df, on=['doi', 'author_name'], how='left')

    column_order = [
        'doi',
        'author_name',
        'given_name',
        'family_name',
        'keyword',
        'pubmed_id',
        'affiliation',
        'institute',
        'address'
    ]

    # Reordering columns if needed and ensuring all columns exist
    column_order = [col for col in column_order if col in merged_df.columns]
    merged_df = merged_df[column_order].drop_duplicates()

    # Save to CSV
    merged_df.to_csv('joined_authors_with_official_address.csv', index=False, encoding='utf-8')

    return merged_df


# address_df = create_authors_address_table()
# print(address_df)

# SMALLER TESTS:
# test_name = format_author_name("Anastasia M.W.", "Cooper")
# print(test_name)

# doi_list = ["10.1016/j.pestbp.2019.08.002"]
# test_df = get_authors_name(doi_list)
# print(test_df)

# doi_list = ["10.1177/0300985817698207", "10.1128/jb.173.10.3101-3108.1991"]
# papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv', dtype={'doi': str})
# crossref_data = query_crossref(doi_list, papers_df)
# print("QUERY VIA CROSSREF:", crossref_data)
