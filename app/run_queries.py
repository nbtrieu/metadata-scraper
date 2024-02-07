import pandas as pd

from get_address import search_place, get_address, get_address_bulk
from run_pubmed_queries import query_pubmed

# my_api_key = 'AIzaSyBeVCa6qSE3QnzaVN4QvVIZWGNAjpvHTGk'

# pmid_list = ['37444255', '37734358']
# # all_results = query_pubmed(pmid_list, 'i')

# doi_list = ["10.1038/s41598-023-47332-0", "10.3390/molecules28186548", "10.3389/fmicb.2023.1121720"]
# all_results = query_pubmed(doi_list, 'd')

# NEXT STEPS:
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

# for result in all_results:
#     search_result = search_place(result, my_api_key)
#     print(f'>>> SEARCH RESULT FOR {result}:', search_result)
#     address = get_address(result)
#     print(f'>>> ADDRESS OF {result}:', address)
#     address_list.append(address)

# address_list = get_address_bulk(all_results)
# # print('+++++ QUERY VIA PMID:', all_results)
# # print("***** ADDRESS LIST:", address_list)

# # Convert the list of dictionaries to a DataFrame
# df = pd.DataFrame(address_list)

# # Remove duplicate rows based on all columns
# df_unique = df.drop_duplicates()

# # Alternatively, we can remove duplicates based on specific columns:
# # df_unique = df.drop_duplicates(subset=['affiliation', 'institute', 'address'])

# # Print the DataFrame before removing duplicates
# print("DataFrame before removing duplicates:")
# print(df)

# # Print the DataFrame after removing duplicates
# print("DataFrame after removing duplicates:")
# print(df_unique)

# df_unique.to_csv('address_list_doi.csv', sep=',', columns=['affiliation', 'institute', 'address'], header=True, index=False, encoding='utf-8')


def retrieve_address_pubmed(data_list: list, command_flag: str):
    pubmed_data = query_pubmed(data_list, command_flag)
    address_list = get_address_bulk(pubmed_data)
    address_df = pd.DataFrame(address_list)
    address_df_unique = address_df.drop_duplicates()
    address_df_unique.to_csv(
        'complete_address_list.csv',
        sep=',',
        columns=['author_name', 'affiliation', 'institute', 'address'],
        header=True,
        index=False,
        encoding='utf-8'
    )


papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv')
doi_list = papers_df['doi'].tolist()
retrieve_address_pubmed(doi_list, 'd')
