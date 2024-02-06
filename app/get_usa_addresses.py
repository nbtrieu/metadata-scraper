import pandas as pd

df = pd.read_csv('full_address_list.csv')

filtered_df = df[df['address'].str.contains("USA", na=False)]

usa_addresses = filtered_df['address'].tolist()

filtered_df.to_csv('usa_address_list.csv', sep=',', columns=['address'], header=True, index=False, encoding='utf-8')
