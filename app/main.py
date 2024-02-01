from get_address import search_place, get_address
from run_pubmed_queries import get_affiliations

my_api_key = 'AIzaSyBeVCa6qSE3QnzaVN4QvVIZWGNAjpvHTGk'
address_list = []

pmid_list = ['37444255', '37734358']
all_affiliations = get_affiliations(pmid_list, 'i')
print('QUERY VIA PMID:', all_affiliations)

for affiliation in all_affiliations:
    # search_result = search_place(affiliation, my_api_key)
    # print('>>> SEARCH RESULT:', search_result)
    address = get_address(affiliation)
    # print('>>> ADDRESS:', address)
    address_list.append(address)

print("ADDRESS LIST:", address_list)
