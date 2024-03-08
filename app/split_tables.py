import pandas as pd


def split_csv_into_smaller_files(csv_file_path, number_of_files=4):
    # Load the CSV file
    df = pd.read_csv(csv_file_path)

    # Calculate the total number of rows and the base number of rows per file
    total_rows = len(df)
    rows_per_split = total_rows // number_of_files
    extra_rows = total_rows % number_of_files  # Calculate any extra rows

    # Split and save the files
    for i in range(number_of_files):
        start_index = i * rows_per_split + min(i, extra_rows)
        if i < number_of_files - 1:
            # Allocate an extra row to this file if i is less than the number of extra rows
            end_index = start_index + rows_per_split + (1 if i < extra_rows else 0)
        else:
            # The last file includes any remaining rows
            end_index = total_rows

        # Extract the subset of the DataFrame
        df_subset = df.iloc[start_index:end_index]

        # Save the subset to a new CSV file
        output_file_path = f'data/split_tables/split_{i+1}.csv'
        df_subset.to_csv(output_file_path, index=False)
        print(f'Saved: {output_file_path}')


# Specify the path to your CSV file
csv_file_path = 'data/2019-2023_Leads_List_Test_deduped.csv'
split_csv_into_smaller_files(csv_file_path)
