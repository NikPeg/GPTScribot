from config import DEBUG, ADMIN


MAX_MESSAGE_LENGTH = 4096


def log(text, bot=None):
    try:
        if not text:
            return
        if DEBUG:
            print(text)
        if bot:
            for i in range(0, len(text), MAX_MESSAGE_LENGTH):
                bot.send_message(ADMIN, text[i:i + MAX_MESSAGE_LENGTH])
    except Exception:
        pass
