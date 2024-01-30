import subprocess


def run_pubmed_queries(pmids):
    script_path = "pubmedAuthorAffiliation/pubmedAuthorAffiliation.py"
    for pmid in pmids:
        try:
            command = f'poetry run python {script_path} -i {pmid}'
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while processing PMID {pmid}: {e}")


def get


# Test
pmid_list = ['37444255', '37734358', '36800030']
run_pubmed_queries(pmid_list)
