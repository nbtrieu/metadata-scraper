import pandas as pd

# papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv')
# keywords_dict = papers_df.set_index('pmid')['keyword'].to_dict()

df = pd.read_csv('official_address_list.csv')

filtered_df = df[df['address'].str.contains("USA", na=False)]

filtered_df.to_csv(
    'official_usa_address_list.csv',
    sep=',',
    columns=[
        'keyword',
        'pubmedId',
        'articleTitle',
        'author_name',
        'affiliation',
        'institute',
        'address'
    ],
    header=True,
    index=False,
    encoding='utf-8'
)
