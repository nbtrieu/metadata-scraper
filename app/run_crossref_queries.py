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


def get_authors_name(doi_list: list):
    authors_names = []

    for doi in tqdm(doi_list, desc="Querying Crossref Authors' Names"):
        url = f"https://api.crossref.org/works/{doi}"
        headers = {"User-Agent": "Email example@example.com"}  # Change to your actual email
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result_dict = response.json()['message']

            authors_list = result_dict.get('author', [])
            for author in authors_list:
                author_dict = {
                    'doi': doi,
                    'given_name': author.get('given', "Unknown"),
                    'family_name': author.get('family', "Unknown"),
                }
                authors_names.append(author_dict)  # Corrected line: append inside the loop

        else:
            print(f"Error fetching data for DOI {doi}: {response.status_code}, {response.text}")

    authors_df = pd.DataFrame(authors_names)
    authors_df_unique = authors_df.drop_duplicates()
    authors_df_unique.to_csv(
        'authors_names_list.csv',
        sep=',',
        columns=['doi', 'given_name', 'family_name'],
        header=True,
        index=False,
        encoding='utf-8'
    )
    return authors_df_unique


papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv', dtype={'doi': str})
doi_list = papers_df['doi'].tolist()
authors_names_df = get_authors_name(doi_list)
official_address_df = pd.read_csv('official_address_list.csv')

# Joining the DataFrames
merged_df = pd.merge(official_address_df, authors_names_df, on='doi', how='left')

column_order = ['keyword', 'pubmed_id', 'doi', 'author_name', 'given_name', 'family_name', 'affiliation', 'institute', 'address']
merged_df.to_csv('joined_official_address_authors.csv', index=False, columns=column_order, encoding='utf-8')

# doi_list = ["10.1177/0300985817698207", "10.1128/jb.173.10.3101-3108.1991"]
# papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv', dtype={'doi': str})
# crossref_data = query_crossref(doi_list, papers_df)
# print("QUERY VIA CROSSREF:", crossref_data)
