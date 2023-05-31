from config import DEBUG, ADMIN


def log(text, bot=None):
    if not text:
        return
    if DEBUG:
        print(text)
    if bot:
        bot.send_message(ADMIN, text)
