# %%
import pandas as pd
import os


# %%
def split_csv(original_csv: str, output_file_path: str):
    # Ensure the output directory exists
    os.makedirs(output_file_path, exist_ok=True)

    # Read the original CSV file
    df = pd.read_csv(original_csv)

    # Determine the number of rows per smaller CSV file
    num_rows = len(df)
    rows_per_file = num_rows // 10
    remainder = num_rows % 10

    # Split the DataFrame and save smaller CSV files
    for i in range(2):
        start_row = i * rows_per_file
        if i == 1:  # Last file includes the remainder rows
            end_row = start_row + rows_per_file + remainder
        else:
            end_row = start_row + rows_per_file
        
        # Slice the DataFrame
        df_small = df.iloc[start_row:end_row]
        
        # Construct the output file path
        output_csv = os.path.join(output_file_path, f'smaller_csv_file_{i+1}.csv')
        
        # Save the smaller DataFrame to a CSV file
        df_small.to_csv(output_csv, index=False)

    print("CSV files have been successfully divided.")



# %% 
split_csv('./data/zebrafish/zebrafish.csv', './data/zebrafish')


# %%
def split_pickle(original_pickle: str, output_file_path: str):
    # Ensure the output directory exists
    os.makedirs(output_file_path, exist_ok=True)

    # Read the original pickle file
    df = pd.read_pickle(original_pickle)

    # Determine the number of rows per smaller CSV file
    num_rows = len(df)
    rows_per_file = num_rows // 10
    remainder = num_rows % 10

    # Split the DataFrame and save smaller CSV files
    for i in range(2):
        start_row = i * rows_per_file
        if i == 1:  # Last file includes the remainder rows
            end_row = start_row + rows_per_file + remainder
        else:
            end_row = start_row + rows_per_file
        
        # Slice the DataFrame
        df_small = df.iloc[start_row:end_row]
        
        # Construct the output file path
        output_pickle = os.path.join(output_file_path, f'smaller_pickle_file_{i+1}.pkl')
        
        # Save the smaller DataFrame to a pickle file
        df_small.to_pickle(output_pickle)

    print("Pickle file has been successfully divided.")


# %%
split_pickle('./outputs/rabbit/rabbit_authors_5.pkl', './outputs/rabbit')

# %%
authors_df = pd.read_pickle('./outputs/rabbit/rabbit_authors_7_1.pkl')
print(authors_df)

# %%
source_df = pd.read_csv('./data/rabbit/smaller_csv_file_7.csv')
print(source_df)

# %%
