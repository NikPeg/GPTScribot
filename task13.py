import re
import string


def check_password(password):
    if len(password) < 8 or len(password) > 18:
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!-~]', password):
        return False
    if re.search(r'\s', password):
        return False
    if len(re.findall(r'\d', password)) < 2:
        return False
    if len(re.findall(r'[a-z]', password)) < 2:
        return False
    if len(re.findall(r'[A-Z]', password)) < 1:
        return False
    if len(re.findall("[" + re.escape(string.punctuation) + "]", password)) < 1:
        return False
    return True


N = int(input())
passwords = [input() for _ in range(N)]

for password in passwords:
    if check_password(password):
        print(1, password)
    else:
        print(0, password)
