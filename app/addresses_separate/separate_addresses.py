#%%
import pandas as pd
import os
import re
from tqdm import tqdm
import csv

#%%
def process_addresses(file_path, output_directory):
    data = pd.read_csv(file_path, dtype={'Zip Code': str})

    # Filter conditions for address and email
    data = data[data['address'].str.contains('USA', na=False, case=True)]
    data = data[~data['Email'].str.contains('cn|jp|mx|pk|qa|ac|ao|dk|gr|au|br|in|fr|co|ch|pl|to|ch|il|it|es|pt|bg|sk|ie|hu|ca|hk|za|nz|fi|nl|be|mo|tw|sa|uk|se|sg|kr|de|no', na=False, case=False) & data['Email'].notna()]
    data = data[~data['Organization'].str.contains('Jiangsu|Rlr Va|Addenbrooke|Ningbo|Adelaide|Monash|Sungkyunkwan|Nantong|Jiuzhou|Catania|Huazhong|Peking|Seoul|Macau|Dalian|Soochow|Hunan|Cedars-Sinai|Tongren|Hainan|Yat-sen|Yonsei|Wuhan|Hebei|Jilin|Nanjing|Guangzhou|Luoyang|Hubei|Ruijin|Huizhou|Luzhou|Jimei|Sichuan|Guangdong|Shandong|Anhui|Shanghai|Yantai|Qingdao|Jiujiang|Jiangxi|Qiongzhou|Shenyang|Zhejiang|Beijing|Kunming|Chongqing|Chengdu|Shantou|Tianjin|Zunyi|Zhengzhou|Henan|Guangxi|Zhongkai|Hong Kong|Shaanxi|Fujian|Jiangnan|Tsinghua|Renji|Fudan|China|Nankai|Yangzhou|Changhai|Shanxi|Mgi|Shenzhen|Chinese', na=False, case=False)]

    data['Street Address'] = ''
    data['City'] = ''
    data['State'] = ''
    data['Zip Code'] = ''
    data['Country'] = 'USA'  

    for index, row in data.iterrows():
       # Use regex to extract the state and zip code
       state_zip_pattern = re.search(r'([A-Z]{2})\s+(\d{5})', row['address'])
       if state_zip_pattern:
           data.at[index, 'State'] = state_zip_pattern.group(1)
           extracted_zip = state_zip_pattern.group(2)
           formatted_zip = f"{extracted_zip:0>5}"  
           data.at[index, 'Zip Code'] = formatted_zip

           parts = [part.strip() for part in row['address'][:state_zip_pattern.start()].split(',')]
           parts = [part for part in parts if part]  # Remove any empty strings

           if len(parts) > 0:
               data.at[index, 'City'] = parts[-1]  
           if len(parts) > 1:
               data.at[index, 'Street Address'] = ', '.join(parts[:-1]) 
           elif len(parts) == 1:
               data.at[index, 'Street Address'] = ''

    data['Zip Code'] = data['Zip Code'].astype(str)
    base_filename = os.path.splitext(os.path.basename(file_path))[0] + '_sep.csv'
    output_file_path = os.path.join(output_directory, base_filename)
    
    data.to_csv(output_file_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f'Processed {len(data)} rows from {base_filename}')

#%%
def process_all_files(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    files = [f for f in os.listdir(input_directory) if f.endswith('.csv')]
    for filename in tqdm(files, desc="Separation Progress"):
        file_path = os.path.join(input_directory, filename)
        process_addresses(file_path, output_directory)

#%%
# Example usage/Change input and output dir everytime 
input_directory = '/Users/oceanuszhang/Desktop/scraper/metadata-scraper/app/addresses_separate/input_addresses/porcine'
output_directory = '/Users/oceanuszhang/Desktop/scraper/metadata-scraper/app/addresses_separate/output_addresses/porcine'
process_all_files(input_directory, output_directory)


# %%
def combine_csv_files(output_directory, combined_file):
    data_frames = []

    if not os.path.exists(output_directory):
        print("Output directory does not exist.")
        return

    try:
        for filename in os.listdir(output_directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(output_directory, filename)
                data_frame = pd.read_csv(file_path, dtype={'Zip Code': str})
                data_frames.append(data_frame)
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        combined_df['Zip Code'] = combined_df['Zip Code'].astype(str)

        combined_df.to_csv(combined_file, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"Combined file saved as {combined_file}")
    else:
        print("No CSV files found in the directory.")

#%%
# Change input and output dir everytime 
output_directory = '/Users/oceanuszhang/Desktop/scraper/metadata-scraper/app/addresses_separate/output_addresses/porcine'
combined_file = '/Users/oceanuszhang/Desktop/scraper/metadata-scraper/app/addresses_separate/combined_addresses/porcine/porcine_combined.csv'
combine_csv_files(output_directory, combined_file)

# %%

