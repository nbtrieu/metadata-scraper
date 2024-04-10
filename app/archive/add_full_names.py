import pandas as pd

file_path = '/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/official_full_name_usa_addresses.csv'
data = pd.read_csv(file_path)

# Adding a "full_name" column by combining "given_name" and "family_name"
data['full_name'] = data['given_name'] + ' ' + data['family_name']

data.head()

output_file_path = '/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/updated_full_name_usa_addresses.csv'
data.to_csv(output_file_path, index=False)

print(f"File saved to: {output_file_path}")
