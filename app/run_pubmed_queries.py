import subprocess


# function to extract 'affiliation' field value from each object in 'authorList' [] and remove the '.' at the end!
def get_affiliation(result_dict):
    pass

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
pmid_list = ['37444255', '37734358', '36800030']
print('QUERY VIA PMIDS:')
query_via_pmid(pmid_list)

# doi_list = ['10.1016/j.molcel.2016.11.013', '10.3389/fmicb.2023.1194606']
# print('QUERY VIA DOIS:')
# query_via_doi(doi_list)
