from gpt_messages import DOLLAR_QUESTION

USELESS_SYMBOLS = {
    '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ' ', 'Глава', 'глава', '(дополнительная глава)'
}
SECTION = "\\section"
BIBLIOGRAPHY_SECTION = "\\section"
SPECIAL_SYMBOLS = {"%"}
BIBLIOGRAPHY_SPECIAL_SYMBOLS = {"$", "&", "_", "%"}
USELESS_SEQUENCES = {"\\url", "[label={[\\arabic*]}]", "\\begin{document}", "\\end{document}", "\\newpage"}
BIBLIOGRAPHIES = {"Библиография", "Список использованных источников", "Источники", "Материалы", "Список литературы",
                  "Список используемой литературы и источников информации", "Список использованной литературы"}
NEW_LINE = "\\\\\n"
BLANK_LINE = "\\\\\n~\\\\\n"
BIG_INDENT = "~\\\\\n~\\\\\n~\\\\\n"
BLANK_LINE_LEN = len(BLANK_LINE)
NEW_PAGE = "\n\\newpage\n"
END_DOCUMENT = "\n\\end{document}"
NAME_USELESS_SYMBOLS = {'.', '"', "'", "?", ":", " "}
USELESS_START_STRING = "Название работы"
SYMBOLS_TO_REPLACE = {
    '"': '"{}',
}
SYMBOLS_TO_ASK = {
    '\\$': DOLLAR_QUESTION,
}
RUSSIAN_SECTION = "Раздел"
BEGINS_WITHOUT_NEW_LINES = {"\\begin", "\\end", "\\subsection", "\\subsubsection", "\\item", "\\bibitem", }
ENDS_WITHOUT_NEW_LINES = {"\\", "}", "]", "\\hline", "\\centering", "&"}
RUSSIAN = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
PICTURE_SUBSTRING = "\\begin{figure}"
DIPLOMA_SUBSTRING = "иплом"
TABLE_OPEN_SUBSTRING = "\\begin{table}"
TABLE_CLOSE_SUBSTRING = "\\end{table}"
REGRET_SUBSTRING = "К сожалению"
SAMPLE_WORKS = [
    "Влияние интернет-мемов на современную политику",
    "Супергерои и их вклад в развитие физической культуры и спорта",
    "Влияние кофе на продуктивность студентов в период сессии",
    "Социальная адаптация зомби в современном обществе (на примере сериала 'Ходячие мертвецы')",
    "Влияние аниме на формирование эстетических предпочтений молодежи",
    "Социальная роль пиццы в жизни студента",
    "Влияние смайликов на эффективность текстовых сообщений",
    "Как музыка из 'Гарри Поттера' влияет на уровень стресса у студентов",
    "Психологический портрет современного геймера",
    "Социальные сети как новая форма искусства",
    "Психология котов: почему они так любят коробки?",
    "Зомби-апокалипсис: теоретический анализ возможных сценариев",
    "Сравнительный анализ домашних питомцев: кто лучше — кошки или собаки?",
]
USELESS_SUBSTRING = "список глав"
