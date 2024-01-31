import subprocess


# function to extract 'affiliation' field value from each object in 'authorList' [] and remove the '.' at the end!
def get_affiliation(result_dict):
    """
    Extract and format the 'affiliation' values from the 'authorList' in 'result_dict'.

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


# call get_affiliation() in both the query functions below
def query_via_pmid(pmids):
    script_path = "pubmedAuthorAffiliation/pubmedAuthorAffiliation.py"
    for pmid in pmids:
        try:
            command = f'poetry run python {script_path} -i {pmid}'
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while processing PMID {pmid}: {e}")


def query_via_doi(dois):
    script_path = "pubmedAuthorAffiliation/pubmedAuthorAffiliation.py"
    for doi in dois:
        try:
            command = f'poetry run python {script_path} -d {doi}'
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while processing DOI {doi}: {e}")


# Test
# pmid_list = ['37444255', '37734358', '36800030']
# print('QUERY VIA PMIDS:')
# query_via_pmid(pmid_list)

# doi_list = ['10.1016/j.molcel.2016.11.013', '10.3389/fmicb.2023.1194606']
# print('QUERY VIA DOIS:')
# query_via_doi(doi_list)

test_dict = {'error': False, 'pubmedId': '36800030', 'journalTitle': 'Applied microbiology and biotechnology', 'articleTitle': 'Distinct roles of carbohydrate-binding modules in multidomain β-1,3-1,4-glucanase on polysaccharide degradation.', 'authorList': [{'firstName': 'n/a', 'initials': 'HI', 'lastName': 'Hamouda', 'affiliation': 'Processes Design and Development Department, Egyptian Petroleum Research Institute, Nasr City, Cairo, 11727, Egypt.', 'country': 'Egypt', 'institute': 'Egyptian Petroleum Research Institute'}, {'firstName': 'n/a', 'initials': 'YX', 'lastName': 'Fan', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Abdalla', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'H', 'lastName': 'Su', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Lu', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lvming@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}, {'firstName': 'n/a', 'initials': 'FL', 'lastName': 'Li', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lifl@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}]}
{'error': False, 'pubmedId': '36800030', 'journalTitle': 'Applied microbiology and biotechnology', 'articleTitle': 'Distinct roles of carbohydrate-binding modules in multidomain β-1,3-1,4-glucanase on polysaccharide degradation.', 'authorList': [{'firstName': 'n/a', 'initials': 'HI', 'lastName': 'Hamouda', 'affiliation': 'Processes Design and Development Department, Egyptian Petroleum Research Institute, Nasr City, Cairo, 11727, Egypt.', 'country': 'Egypt', 'institute': 'Egyptian Petroleum Research Institute'}, {'firstName': 'n/a', 'initials': 'YX', 'lastName': 'Fan', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Abdalla', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'H', 'lastName': 'Su', 'affiliation': 'Qingdao C1 Refinery Engineering Research Center, Qingdao Institute of Bioenergy and Bioprocess Technology, Chinese Academy of Sciences, Qingdao, 266101, China.', 'country': 'China', 'institute': 'Qingdao Institute of Bioenergy and Bioprocess Technology'}, {'firstName': 'n/a', 'initials': 'M', 'lastName': 'Lu', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lvming@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}, {'firstName': 'n/a', 'initials': 'FL', 'lastName': 'Li', 'affiliation': 'Shandong Energy Institute, Qingdao, 266101, China. lifl@qibebt.ac.cn.', 'country': 'China', 'institute': 'Shandong Energy Institute'}]}
affiliation_list = get_affiliation(test_dict)
print(affiliation_list)
