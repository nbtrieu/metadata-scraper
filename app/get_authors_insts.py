from crossref.restful import Works

works = Works()


def get_institution(doi):
    full_doi = works.doi(doi)
    author_list = full_doi['author']
    print("AUTHORS:", author_list)

    institution_set = set()

    for author in author_list:
        if 'affiliation' in author and author['affiliation']:
            institution_name = author['affiliation'][0]['name']
            institution_set.add(institution_name)

    institution_list = list(institution_set)
    return institution_list


# Test:
institutions = get_institution("10.1111/j.1750-3841.2007.00549.x")
print(institutions)
