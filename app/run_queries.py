import pandas as pd
import json
from tqdm import tqdm
from get_address import get_address_from_pubmed, get_address_from_crossref
from run_pubmed_queries import query_pubmed
from run_crossref_queries import query_crossref

"""
ask GPT to give PMIDs or DOIs of research papers focusing on the keywords
compile two CSV tables: article_name | PMID & article_name | DOI
get a list of PMIDs + a list of DOIs from the respective CSV columns
ADD TQDM TO TRACK PROGRESS!!!!
call query_pubmed on each list
combine all results into all_results []
pass in all_results list to get_address_bulk etc.

NEXT STEPS:
filter for full address
connect with authors
make 1 slide with flowchart of my workflow for today's meeting
find API to get authors' email addresses

create a portal to ingest data collected through this process
list of keywords -> plug in pubmed advanced query (Nature, Science, Cell) -> get authors,affiliation,etc
put the authors,affiliation,addresses + connected to keywords -> graph db (person/article nodes)
might use GPT to search for keywords in abstracts, zymo kits in method sections later
"""

with open('config.json', 'r') as file:
    config = json.load(file)
google_maps_places_api_key = config['apiKeys']['googleMapsPlaces']

papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv', dtype={'pmid': str})

pmids_list = papers_df['pmid'].tolist()
print(">>> PMID LIST:", pmids_list)
pubmed_data = query_pubmed(pmids_list, 'i', papers_df)
# print("QUERY VIA PMID:", pubmed_data)
if pubmed_data:
    print("First 3 elements of pubmed_data list:")
    for data in pubmed_data[:3]:
        print(data)

# dois_list = papers_df['doi'].tolist()
# crossref_data = query_crossref(dois_list, papers_df)


def compile_table(publications_list: list):
    all_results = []

    for publication in tqdm(publications_list, desc="Making Table"):
        publication_results = []  # Storing results for each publication separately

        if "authorList" not in publication:
            print(f"Skipping publication {publication.get('pubmedId', 'Unknown')} due to missing 'authorList'")
            continue

        # Extracting 'keyword' and 'pubmedId' from the publication
        keyword = publication.get("keyword", "Unknown")
        pubmedId = publication.get("pubmedId", "Unknown")
        # articleTitle = publication.get("articleTitle", "Unknown")
        original_articleTitle = publication.get("articleTitle", "Unknown")
        articleTitle = original_articleTitle.replace('.', '') if original_articleTitle is not None else "Unknown"
        print(f'ARTICLE TITLE FOR PMID {pubmedId}:', articleTitle)

        for author in publication["authorList"]:
            for key in ['affiliation', 'institute']:
                if author.get(key, "") == "Unparsed":  # Skip 'Unparsed' institute values
                    continue

                result_dict = {
                        "keyword": keyword,
                        "pubmedId": pubmedId,
                        "articleTitle": articleTitle,
                        "author_name": f"{author.get('lastName', '')} {author.get('initials', '')}".strip(),
                        "affiliation": author.get('affiliation', "Unspecified"),
                        "institute": author.get('institute', "Unparsed"),
                    }

                publication_results.append(result_dict)
                break

        all_results.extend(publication_results)

    result_df = pd.DataFrame(all_results)
    result_df_unique = result_df.drop_duplicates()
    result_df_unique.to_csv(
        'testing_list.csv',
        sep=',',
        columns=['keyword', 'pubmedId', 'articleTitle', 'author_name', 'affiliation', 'institute'],
        header=True,
        index=False,
        encoding='utf-8'
    )


def create_address_table_from_pubmed(pubmed_data: list):
    address_list = get_address_from_pubmed(pubmed_data, google_maps_places_api_key)
    address_df = pd.DataFrame(address_list)
    address_df_unique = address_df.drop_duplicates()
    address_df_unique.to_csv(
        'pubmed_address_list_new.csv',
        sep=',',
        columns=['keyword', 'pubmed_id', 'doi', 'author_name', 'affiliation', 'institute', 'address'],
        header=True,
        index=False,
        encoding='utf-8'
    )


def create_address_table_from_crossref(crossref_data: list):
    address_list = get_address_from_crossref(crossref_data, google_maps_places_api_key)
    address_df = pd.DataFrame(address_list)
    address_df_unique = address_df.drop_duplicates()
    address_df_unique.to_csv(
        'crossref_address_list.csv',
        sep=',',
        columns=['doi', 'keyword', 'given_name', 'family_name', 'affiliation', 'address'],
        header=True,
        index=False,
        encoding='utf-8'
    )


create_address_table_from_pubmed(pubmed_data)
# create_address_table_from_crossref(crossref_data)
