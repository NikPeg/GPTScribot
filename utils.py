from config import DEBUG


def log(text):
    if DEBUG:
        print(text)
