import pandas as pd


def get_domain(email: str) -> str:
    return email.split("@")[1].lower()


def get_last_name(name: str) -> str:
    return name.split()[-1].lower().capitalize()


def get_first_name(name: str) -> str:
    char_arr = name.split()
    first_name = char_arr[0].lower().capitalize()
    if len(char_arr) >= 3:
        middle_chars = char_arr[1:-1]
        middle_name = ' '.join(middle_chars)
        first_name = first_name + ' ' + middle_name

    return first_name


# example_email = "RISIMON@MEDNET.UCLA.EDU"
# test_domain = get_domain(example_email)
# print(test_domain)

example_name = "Susanne de la NICHTERWITZ"
test_first_name = get_first_name(example_name)
test_last_name = get_last_name(example_name)
print(test_first_name)
print(test_last_name)

# middle_chars = ["john", "blah", "bleh", "doe"][1:-1]
# print(' '.join(middle_chars))
