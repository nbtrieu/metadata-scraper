import subprocess
import json
import pandas as pd
from tqdm import tqdm


def get_metadata(result_dict: dict):
    """
    Extracts/formats relevant values from the 'authorList' in 'result_dict'.

    Parameters:
    result_dict (dict): A dictionary containing an 'authorList'.

    Returns:
    list: A list of dicts.
    """
    if "authorList" not in result_dict:
        print("No 'authorList' key in the dictionary.")
        return []

    all_metadata = []

    pmid = result_dict.get("pubmedId")

    for author in result_dict["authorList"]:
        author_name = author.get("lastName") + " " + author.get("initials") if author.get("lastName") and author.get("initials") else None
        affiliation = author.get("affiliation", None)
        institute = author.get("institute", None)

        author_data = {
            "author_name": author_name,
            "affiliation": affiliation,
            "institute": institute
        }

        all_metadata.append(author_data)

    return all_metadata


def query_pubmed(ids_list: list, command_flag: str, keywords_dict: dict):
    """
    Queries the pubmedAuthorAffiliation.py script for authors' affiliations based on PMIDs or DOIs.

    Parameters:
    values (list): A list of strings, each being a PMID or DOI to query.
    command_flag (str): 'i' to query by PMID, 'd' to query by DOI.

    Returns:
    list: A list of dictionaries, each with 'affiliation' and 'institute' keys for the queries.
    """

    if command_flag not in ['i', 'd']:
        print("Invalid command flag. Please input either 'i' for PMID or 'd' for DOI.")
        return []

    script_path = "pubmedAuthorAffiliation/pubmedAuthorAffiliation.py"
    all_results = []

    for value in tqdm(ids_list, desc="Querying PubMed"):
        try:
            command = f'poetry run python {script_path} -{command_flag} {value}'
            result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
            # print("Attempting to parse JSON:", result[:500])
            result_dict = json.loads(result)

            keyword = keywords_dict.get(value, 'Keyword Not Found')
            result_dict['keyword'] = keyword

            all_results.append(result_dict)

        except subprocess.CalledProcessError as e:
            valueType = "PMID" if command_flag == 'i' else "DOI"
            print(f"An error occurred while processing {valueType} {value}: {e}")
        except json.JSONDecodeError as e:
            valueType = "PMID" if command_flag == 'i' else "DOI"
            print(f"Failed to parse JSON from output for {valueType} {value}: {e}")

    return all_results


# CHECKS:
pmid_list = ['7275933', '37110241']

papers_df = pd.read_csv('/Users/nicoletrieu/Documents/zymo/metadata-scraper/app/data/relevant_papers.csv')
papers_df['pmid'] = papers_df['pmid'].apply(lambda x: str(int(x)) if pd.notnull(x) and x.is_integer() else str(x))
keywords_dict = papers_df.set_index('pmid')['keyword'].to_dict()
print('>>> KEYWORDS DICT:', keywords_dict)

pubmed_data = query_pubmed(pmid_list, 'i', keywords_dict)
print('QUERY VIA PMID:', pubmed_data)

# doi_list = ['10.1016/j.molcel.2016.11.013', '10.3389/fmicb.2023.1194606']
# all_affiliations = query_pubmed(doi_list, 'd')
# print('QUERY VIA DOI:', all_affiliations)

# test_dict = {'error': False, 'pubmedId': '36800030', 'journalTitle': 'Applied microbiology and biotechnology', 'articleTitle': 'Distinct roles of carbohydrate-binding modules in multidomain β-1,3-1,4-glucanase on polysaccharide degradation.', 'authorList': [{'firstName': 'n/a', 'initials': 'HI', 'lastName': 'Hamouda', 'affiliation': 'Processes Design and Development Department, Egyptian Petroleum Research Institute, Nasr City, Cairo, 11727, Egypt.', 'country': 'Egypt', 'institute': 'Egyptian Petroleum Research Institute'}, {'firstName': 'n/a', 'initials': 'YX', 'lastName': 'Fan', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Abdalla', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'H', 'lastName': 'Su', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Lu', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lvming@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}, {'firstName': 'n/a', 'initials': 'FL', 'lastName': 'Li', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lifl@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}]}
# {'error': False, 'pubmedId': '36800030', 'journalTitle': 'Applied microbiology and biotechnology', 'articleTitle': 'Distinct roles of carbohydrate-binding modules in multidomain β-1,3-1,4-glucanase on polysaccharide degradation.', 'authorList': [{'firstName': 'n/a', 'initials': 'HI', 'lastName': 'Hamouda', 'affiliation': 'Processes Design and Development Department, Egyptian Petroleum Research Institute, Nasr City, Cairo, 11727, Egypt.', 'country': 'Egypt', 'institute': 'Egyptian Petroleum Research Institute'}, {'firstName': 'n/a', 'initials': 'YX', 'lastName': 'Fan', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Abdalla', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'H', 'lastName': 'Su', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Lu', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lvming@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}, {'firstName': 'n/a', 'initials': 'FL', 'lastName': 'Li', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lifl@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}]}
# affiliation_list = get_affiliation(test_dict)
# print(affiliation_list)
