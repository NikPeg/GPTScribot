from config import DEBUG, ADMIN


def log(text, bot=None):
    if DEBUG:
        print(text)
    if bot:
        bot.send_message(ADMIN, text)
