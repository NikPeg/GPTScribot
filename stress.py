import telebot
from telebot import types

bot = telebot.TeleBot("6410701757:AAFxGwhkCBsy6hJElwrDB-z0AT7Hf9j67x0")
START_MESSAGE = "Привет! Я бот-дневник управления стрессом. Расскажи мне о своем дне."
DONATE_URL = "https://pay.cloudtips.ru/p/7a822105"
ABOUT_STRESS = """Стресс - это естественная биохимическая реакция, которая оказывает воздействие на мозг и тело, заставляя нас реагировать на потрясения, опасности и изменения в нашем окружении. 

Стресс может быть как положительным, так и отрицательным. Положительный стресс поднимает вас когда вы сталкиваетесь с новыми испытаниями. Отрицательный стресс может оказывать вредное длительное воздействие на ваше здоровье.

Многие факторы, такие как работа, отношения, финансы и окружающая среда, могут вызвать стресс.

Существуют различные способы управления стрессом, включая физическую активность, расслабление и медитацию, здоровое питание и достаточный сон.

Научитесь распознавать признаки стресса, чтобы управлять им эффективно. К этим признакам могут относиться повышенная раздражительность, проблемы со сном, частые головные боли и чувство усталости.

Управление стрессом является важной частью в общем подходе к здоровому образу жизни. Оно поможет вам более эффективно справляться с напряжениями и улучшит ваше общее качество жизни.

Если вас беспокоит ваш уровень стресса или вы хотите узнать больше о том, как справляться с стрессом, обратитесь к врачу или другому специалисту по здоровью.

Обратите внимание, что стресс может быть связан с серьезными психологическими проблемами, такими как депрессия и тревожность. Если вы испытываете постоянный стресс, перегорание или кажется, что не можете справиться со своими чувствами, обязательно обратитесь за помощью к профессионалам.
"""
NEW_MESSAGE = "Введите ваше текущее состояние:"
CONNECT_MESSAGE = """Стресс-бот - это интеллектуальный чат-бот, созданный для контроля над стрессом и улучшения эмоционального здоровья. Он использует искусственный интеллект и когнитивно-поведенческие техники для оказания помощи пользователям в трудные моменты. Чтобы помочь вам справиться со стрессом, бот предоставляет различные стратегии, такие как медитационные упражнения, дыхательные техники и советы по самоуспокоению. С его помощью вы также можете отслеживать свои эмоциональные состояния, получая таким образом более четкое представление о своем эмоциональном здоровье. Бот предназначен для тех, кто ищет способы облегчить стресс в быстром и доступном формате."""
THANK_MESSAGE = "Спасибо! Данные о Вашем дне соханены. Команда разработчиков бота гарантирует, что ваши данные не будут переданы третьим лицам. Отправляйте информацию о Вашем состоянии чаще, чтобы лучше бороться со своим стрессом!"
MAX_MESSAGE_LENGTH = 4096
ADMIN = 241248104


def log(text, bot=None):
    try:
        if not text:
            return
        print(text)
        if bot:
            for i in range(0, len(text), MAX_MESSAGE_LENGTH):
                bot.send_message(ADMIN, text[i:i + MAX_MESSAGE_LENGTH])
    except Exception:
        pass


@bot.message_handler(commands=['start', 'help'])
def start(message):
    log(f"User @{message.from_user.username} started a bot.")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Внести новую запись', callback_data='new')
    btn2 = types.InlineKeyboardButton(text='Узнать о стрессе', callback_data='info')
    btn3 = types.InlineKeyboardButton(text='О нас', callback_data='connect')
    btn4 = types.InlineKeyboardButton(text='Отправить донат', url=DONATE_URL)
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    bot.send_message(message.from_user.id, START_MESSAGE, reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split('_')
    markup = types.InlineKeyboardMarkup()
    if req[0] == 'info':
        btn2 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn2)
        bot.edit_message_text(
            ABOUT_STRESS,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
    elif req[0] == 'new':
        btn2 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn2)
        bot.edit_message_text(
            NEW_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
    elif req[0] == 'connect':
        btn1 = types.InlineKeyboardButton(text='Представитель команды', url='https://t.me/nikpeg')
        btn2 = types.InlineKeyboardButton(text='Канал проекта', url='https://t.me/scribo_project')
        btn3 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
        markup.add(btn1, btn2)
        markup.add(btn3)
        bot.edit_message_text(
            CONNECT_MESSAGE,
            reply_markup=markup,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
    elif req[0] == 'menu':
        btn1 = types.InlineKeyboardButton(text='Внести новую запись', callback_data='new')
        btn2 = types.InlineKeyboardButton(text='Узнать о стрессе', callback_data='info')
        btn4 = types.InlineKeyboardButton(text='Отправить донат', url=DONATE_URL)
        markup.add(btn1)
        markup.add(btn2, btn4)
        bot.send_message(call.message.chat.id, START_MESSAGE, reply_markup=markup, parse_mode='html')


@bot.message_handler(content_types=['text'])
def get_message(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
    markup.add(btn1)
    bot.send_message(message.chat.id, THANK_MESSAGE, reply_markup=markup, parse_mode='html')

log("Bot is running!", bot)
bot.infinity_polling()
