# %%
import pandas as pd
import os


# %%
def split_csv(original_csv: str, output_file_path: str, num_parts: int):
    # Ensure the output directory exists
    os.makedirs(output_file_path, exist_ok=True)

    # Read the original CSV file
    df = pd.read_csv(original_csv)

    # Determine the number of rows per smaller CSV file
    num_rows = len(df)
    rows_per_file = num_rows // num_parts
    remainder = num_rows % num_parts

    # Split the DataFrame and save smaller CSV files
    for i in range(num_parts):
        start_row = i * rows_per_file
        if i == num_parts - 1:  # Last file includes the remainder rows
            end_row = start_row + rows_per_file + remainder
        else:
            end_row = start_row + rows_per_file
        
        # Slice the DataFrame
        df_small = df.iloc[start_row:end_row]
        
        # Construct the output file path
        output_csv = os.path.join(output_file_path, f'smaller_csv_file_{i+1}.csv')
        
        # Save the smaller DataFrame to a CSV file
        df_small.to_csv(output_csv, index=False)

    print(f"CSV files have been successfully divided into {num_parts} parts.")



# %% 
# split_csv(original_csv='./data/wheat/wheat.csv', output_file_path='./data/wheat', num_parts=2)

# %%
split_csv(original_csv='./outputs/porcine/porcine_authors_4.csv', output_file_path='./outputs/porcine', num_parts=2)

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
split_pickle('./outputs/wheat/wheat_authors_2.pkl', './outputs/wheat')

# %%
authors_df = pd.read_pickle('./outputs/wheat/wheat_authors_2.pkl')
print(authors_df)
# %%
