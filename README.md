# Metadata Scraper
## 1. Install  `poetry` for package management
Open Integrated Terminal and run `poetry shell` and `poetry install`.

## 2. Import source data
Make new directory inside `data` with distinct name (e.g. "zymolase"). Copy or download source **CSV file** to this new directory and rename file for readability (e.g. "zymolase_leads.csv").

## 3. Create placeholder directory for output file
Make new directory inside `outputs` with distinct name (e.g. "zymolase"). This directory will contain all the files output from our code.

## 4. Get PMIDs and author data from PubMed
Open `get_pmids_and_author_data.py`. 

Go to `source_df` and replace the CSV file name with the current source file name:
> `source_df = pd.read_csv('./data/zymolase/zymolase_leads.csv')`

Rename the output file as well:
> `result_df.to_pickle('./outputs/zymolase/zymolase_authors.pkl')`

Run all active cells from top to bottom (skipping greyed out cells).

## 5. Get mailing addresses from PubMed author data
Open `get_addresses_from_author_data.py`. 

Go to `author_dicts` and replace the value for `pubmed_result_file_path` with the output file name (from step 4) and replace the value for `lead_source_file_path` with the current source file name:

```
author_dicts = process_author_dicts(
    pubmed_result_file_path='./outputs/zymolase/zymolase_authors.pkl',
    lead_source_file_path='./data/zymolase_leads.csv',
    leadsource_lastname_column_name='LastName',
    leadsource_firstname_column_name='FirstName'
)
```

Replace the source CSV file name inside the `lead_source_file_path` parameter and the output CSV file name inside the `output_filename` parameter of the following code block:

```
process_addresses(
    address_dicts=address_dicts,
    lead_source_file_path='./data/zymolase_leads.csv',
    output_filename='./outputs/zymolase/matched_zymolase_addresses.csv'
)
```

Run all active cells from top to bottom (skipping greyed out cells).

Go to the `outputs` directory to retrieve the addresses.
