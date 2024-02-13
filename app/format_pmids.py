import pandas as pd

df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/joined_authors_with_official_address.csv')

# Convert 'pubmed_id' to numeric, coercing errors to NaN, then fill NaN with a placeholder or skip
df['pubmed_id'] = pd.to_numeric(df['pubmed_id'], errors='coerce')

# Fill NaN values with a placeholder, if desired (e.g., 'missing')
# result_df['pubmed_id'] = result_df['pubmed_id'].fillna('missing')

# Convert non-NaN 'pubmed_id' values to int, then to string
df.loc[df['pubmed_id'].notna(), 'pubmed_id'] = df.loc[df['pubmed_id'].notna(), 'pubmed_id'].astype(int).astype(str)

df.to_csv('joined_authors_with_official_address_updated.csv', index=False, encoding='utf-8')
