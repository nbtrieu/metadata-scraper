import pandas as pd

from get_address import get_address_bulk
from run_pubmed_queries import query_pubmed

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

my_api_key = 'AIzaSyBeVCa6qSE3QnzaVN4QvVIZWGNAjpvHTGk'

papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv')
papers_df['pmid'] = papers_df['pmid'].apply(lambda x: str(int(x)) if pd.notnull(x) and x.is_integer() else str(x))
keywords_dict = papers_df.set_index('pmid')['keyword'].to_dict()
print('>>> KEYWORDS DICT:', keywords_dict)
pmid_list = papers_df['pmid'].tolist()
print(">>> PMID LIST:", pmid_list)

pubmed_data = query_pubmed(pmid_list, 'i', keywords_dict)
print('QUERY VIA PMID:', pubmed_data)


def create_address_list(pubmed_data: list):
    address_list = get_address_bulk(pubmed_data, my_api_key)
    address_df = pd.DataFrame(address_list)
    address_df_unique = address_df.drop_duplicates()
    address_df_unique.to_csv(
        'official_address_list.csv',
        sep=',',
        columns=['keyword', 'pubmedId', 'articleTitle', 'author_name', 'affiliation', 'institute', 'address'],
        header=True,
        index=False,
        encoding='utf-8'
    )


create_address_list(pubmed_data)
