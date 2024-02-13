import pandas as pd

# papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv')
# keywords_dict = papers_df.set_index('pmid')['keyword'].to_dict()

df = pd.read_csv('joined_address_authors.csv')

filtered_df = df[df['address'].str.contains("USA", na=False)]

filtered_df.to_csv(
    'joined_usa_address_authors.csv',
    sep=',',
    columns=[
        'keyword',
        'pubmed_id',
        'doi',
        'author_name',
        'affiliation',
        'institute',
        'address',
        'given_name',
        'family_name'
    ],
    header=True,
    index=False,
    encoding='utf-8'
)
