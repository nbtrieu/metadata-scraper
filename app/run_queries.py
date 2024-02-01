import pandas as pd

from get_address import search_place, get_address, get_address_bulk
from run_pubmed_queries import query_pubmed

my_api_key = 'AIzaSyBeVCa6qSE3QnzaVN4QvVIZWGNAjpvHTGk'
# address_list = []

pmid_list = ['37444255', '37734358']
all_results = query_pubmed(pmid_list, 'i')

# for result in all_results:
#     search_result = search_place(result, my_api_key)
#     print(f'>>> SEARCH RESULT FOR {result}:', search_result)
#     address = get_address(result)
#     print(f'>>> ADDRESS OF {result}:', address)
#     address_list.append(address)

address_list = get_address_bulk(all_results)
# print('+++++ QUERY VIA PMID:', all_results)
# print("***** ADDRESS LIST:", address_list)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(address_list)

# Remove duplicate rows based on all columns
df_unique = df.drop_duplicates()

# Alternatively, we can remove duplicates based on specific columns:
# df_unique = df.drop_duplicates(subset=['affiliation', 'institute', 'address'])

# Print the DataFrame before removing duplicates
print("DataFrame before removing duplicates:")
print(df)

# Print the DataFrame after removing duplicates
print("DataFrame after removing duplicates:")
print(df_unique)

df_unique.to_csv('address_list.csv', sep=',', columns=['affiliation', 'institute', 'address'], header=True, index=False, encoding='utf-8')
