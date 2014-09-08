import re

def password_strength_test(password, length=8, upper=True, lower=True, numbers=True):
    return (len(password) >= length and
        (not upper or re.search(r'[A-Z]', password)) and
        (not lower or re.search(r'[a-z]', password)) and
        (not numbers or re.search(r'[0-9]', password)))