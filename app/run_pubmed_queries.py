import subprocess
import json
from tqdm import tqdm


def get_affiliation(result_dict: dict):
    """
    Extracts/formats the 'affiliation' values from the 'authorList' in 'result_dict'.

    Parameters:
    result_dict (dict): A dictionary containing an 'authorList'.

    Returns:
    list: A list of formatted affiliation strings.
    """

    if "authorList" not in result_dict:
        print("No 'authorList' key in the dictionary.")
        return []

    affiliation_list = []

    for author in result_dict["authorList"]:
        affiliation = author.get("affiliation")
        if affiliation:
            formatted_affiliation = affiliation.replace(".", "")
            affiliation_list.append(formatted_affiliation)
            # print(f"Successfully added {formatted_affiliation} to the list")
        else:
            print(f"Affiliation value for {author} does not exist")

    return affiliation_list


def get_institute(result_dict: dict):
    """
    Extracts/formats the 'institute' values from the 'authorList' in 'result_dict'.

    Parameters:
    result_dict (dict): A dictionary containing an 'authorList'.

    Returns:
    list: A list of formatted institute strings.
    """

    if "authorList" not in result_dict:
        print("No 'authorList' key in the dictionary.")
        return []

    institute_list = []

    for author in result_dict["authorList"]:
        institute = author.get("institute")
        if institute:
            institute_list.append(institute)
            # print(f"Successfully added {institute} to the list")
        else:
            print(f"Institute value for {author} does not exist")

    return institute_list


def query_pubmed(values: list, command_flag: str):
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

    for value in tqdm(values, desc="Querying PubMed"):
        try:
            command = f'poetry run python {script_path} -{command_flag} {value}'
            result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
            # print("Attempting to parse JSON:", result[:500])
            result_dict = json.loads(result)
            affiliations = get_affiliation(result_dict)
            institutes = get_institute(result_dict)
            for affiliation, institute in zip(affiliations, institutes):
                all_results.append({"affiliation": affiliation, "institute": institute})

        except subprocess.CalledProcessError as e:
            valueType = "PMID" if command_flag == 'i' else "DOI"
            print(f"An error occurred while processing {valueType} {value}: {e}")
        except json.JSONDecodeError as e:
            valueType = "PMID" if command_flag == 'i' else "DOI"
            print(f"Failed to parse JSON from output for {valueType} {value}: {e}")

    return all_results


# CHECKS:
# pmid_list = ['37444255', '37734358']
# all_affiliations = query_pubmed(pmid_list, 'i')
# print('QUERY VIA PMID:', all_affiliations)

# doi_list = ['10.1016/j.molcel.2016.11.013', '10.3389/fmicb.2023.1194606']
# all_affiliations = query_pubmed(doi_list, 'd')
# print('QUERY VIA DOI:', all_affiliations)

# test_dict = {'error': False, 'pubmedId': '36800030', 'journalTitle': 'Applied microbiology and biotechnology', 'articleTitle': 'Distinct roles of carbohydrate-binding modules in multidomain β-1,3-1,4-glucanase on polysaccharide degradation.', 'authorList': [{'firstName': 'n/a', 'initials': 'HI', 'lastName': 'Hamouda', 'affiliation': 'Processes Design and Development Department, Egyptian Petroleum Research Institute, Nasr City, Cairo, 11727, Egypt.', 'country': 'Egypt', 'institute': 'Egyptian Petroleum Research Institute'}, {'firstName': 'n/a', 'initials': 'YX', 'lastName': 'Fan', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Abdalla', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'H', 'lastName': 'Su', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Lu', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lvming@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}, {'firstName': 'n/a', 'initials': 'FL', 'lastName': 'Li', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lifl@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}]}
# {'error': False, 'pubmedId': '36800030', 'journalTitle': 'Applied microbiology and biotechnology', 'articleTitle': 'Distinct roles of carbohydrate-binding modules in multidomain β-1,3-1,4-glucanase on polysaccharide degradation.', 'authorList': [{'firstName': 'n/a', 'initials': 'HI', 'lastName': 'Hamouda', 'affiliation': 'Processes Design and Development Department, Egyptian Petroleum Research Institute, Nasr City, Cairo, 11727, Egypt.', 'country': 'Egypt', 'institute': 'Egyptian Petroleum Research Institute'}, {'firstName': 'n/a', 'initials': 'YX', 'lastName': 'Fan', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Abdalla', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'H', 'lastName': 'Su', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Lu', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lvming@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}, {'firstName': 'n/a', 'initials': 'FL', 'lastName': 'Li', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lifl@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}]}
# affiliation_list = get_affiliation(test_dict)
# print(affiliation_list)
