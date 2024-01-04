from gpt_messages import AMPERSAND_QUESTION, DOLLAR_QUESTION

USELESS_SYMBOLS = {'-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ' '}
SECTION = "\\section"
BIBLIOGRAPHY_SECTION = "\\section*"
SPECIAL_SYMBOLS = {"%"}
BIBLIOGRAPHY_SPECIAL_SYMBOLS = {"$", "&", "_", "%"}
USELESS_SEQUENCES = {"\\url", "[label={[\\arabic*]}]"}
BIBLIOGRAPHIES = {"Библиография", "Список использованных источников", "Источники", "Материалы", "Список литературы",
                  "Список используемой литературы и источников информации", "Список использованной литературы"}
NEW_LINE = "\\\\\n"
BLANK_LINE = "\\\\\n~\\\\\n"
BIG_INDENT = "~\\\\\n~\\\\\n~\\\\\n"
BLANK_LINE_LEN = len(BLANK_LINE)
NEW_PAGE = "\n\\newpage\n"
END_DOCUMENT = "\n\\end{document}"
NAME_USELESS_SYMBOLS = {'.', '"', "'", "?"}
SYMBOLS_TO_REPLACE = {
    '"': '"{}',
}
SYMBOLS_TO_ASK = {
    '&': AMPERSAND_QUESTION,
    '\\$': DOLLAR_QUESTION,
}
RUSSIAN_SECTION = "Раздел"
BEGINS_WITHOUT_NEW_LINES = {"\\begin", "\\end", "\\subsection", "\\subsubsection", "\\item", "\\bibitem", }
ENDS_WITHOUT_NEW_LINES = {"\\", "}", "]", "\\hline", "\\centering", "&"}
RUSSIAN = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
PICTURE_SUBSTRING = "\\begin{figure}"
DIPLOMA_SUBSTRING = "иплом"
