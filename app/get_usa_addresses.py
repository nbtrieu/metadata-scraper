import pandas as pd

df = pd.read_csv('complete_address_list.csv')

filtered_df = df[df['address'].str.contains("USA", na=False)]

filtered_df.to_csv('usa_address_list.csv', sep=',', 
                   columns=['author_name', 'affiliation', 'institute', 'address'], 
                   header=True, index=False, encoding='utf-8')
