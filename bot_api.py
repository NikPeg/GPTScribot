from telebot.apihelper import ApiTelegramException

from messages import *
from constants import *
from telebot import types

from utils import log


def edit_status_message(message, bot, ready_chapters=0, chapters_count=10):
    if not message:
        return
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='🏠Главное меню', callback_data='menu')
    btn2 = types.InlineKeyboardButton(text='👀Показать процесс', callback_data='show')
    markup.add(btn1)
    markup.add(btn2)
    ready_count = round(ready_chapters / chapters_count * 10)
    text = message.text
    if text.count(READY_SYMBOL) == ready_count:
        return
    try:
        bot.edit_message_text(
            STATUS_MESSAGE.format(ready_count * READY_SYMBOL + UNREADY_SYMBOL * (10 - ready_count)),
            reply_markup=markup,
            parse_mode='Markdown',
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    except Exception as e:
        log(e, bot)
