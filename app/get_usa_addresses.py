import pandas as pd

df = pd.read_csv('joined_authors_with_official_address_updated.csv')

filtered_df = df[df['address'].str.contains("USA", na=False)].drop_duplicates()

filtered_df.to_csv(
    'full_name_usa_address.csv',
    sep=',',
    columns=[
        'doi',
        'author_name',
        'given_name',
        'family_name',
        'keyword',
        'pubmed_id',
        'affiliation',
        'institute',
        'address'
    ],
    header=True,
    index=False,
    encoding='utf-8'
)
