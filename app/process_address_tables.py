# %%
import pandas as pd


def process_csv_files(file1, file2, output_file):
    # Read the CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Combine the dataframes
    combined_df = pd.concat([df1, df2], ignore_index=True)
    
    # Remove rows with empty values in the "address" column
    combined_df = combined_df.dropna(subset=['address'])
    
    # Columns to be removed
    columns_to_remove = [
        'PublishedDate', 'Region', 'State', 'Country', 
        'No. Collaborators', 'Journal/Preprint', 'Journal Research Impact', 
        'Cited', 'ArticleTitle', 'PubMed Link', 'Scileads Profile', 
        'Scileads Publication', 'initials', 'pubmed_affiliation', 'pubmed_institute'
    ]
    
    # Remove the specified columns
    combined_df = combined_df.drop(columns=columns_to_remove)
    
    # Rename the "Organisation" column to "Organization"
    combined_df = combined_df.rename(columns={'Organisation': 'Organization'})
    
    # Deduplicate the remaining rows
    deduplicated_df = combined_df.drop_duplicates()
    
    # Save the processed dataframe to a new CSV file
    deduplicated_df.to_csv(output_file, index=False)
    
    return deduplicated_df


# %%
file1 = './outputs/zebrafish/addresses/matched_zebrafish_addresses_4_1.csv'
file2 = './outputs/zebrafish/addresses/matched_zebrafish_addresses_4_2.csv'
output_file = './outputs/zebrafish/addresses/processed/processed_zebrafish_addresses_4.csv'
processed_df = process_csv_files(file1, file2, output_file)
print(processed_df)

# %%
