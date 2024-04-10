from crossref.restful import Works

works = Works()


def get_institution(doi):
    full_doi = works.doi(doi)
    author_list = full_doi['author']
    print("AUTHORS:", author_list)

    institution_set = set()

    for author in author_list:
        if 'affiliation' in author and author['affiliation']:
            affiliation_list = author['affiliation']
            for affiliation in affiliation_list:
                institution_name = affiliation['name']
                institution_set.add(institution_name)

    institution_list = list(institution_set)
    return institution_list


# Test:
institutions = get_institution("10.3923/ijps.2023.12.16")
print("INSTITUTIONS:", institutions)
