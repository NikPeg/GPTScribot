USELESS_SYMBOLS = {'-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ' '}
SECTION = "\\section"
BIBLIOGRAPHY_SECTION = "\\section*"
SPECIAL_SYMBOLS = {"$", "%"}
BIBLIOGRAPHY_SPECIAL_SYMBOLS = {"$", "&", "_", "%"}
USELESS_SEQUENCES = {"\\url"}
BIBLIOGRAPHIES = {"Библиография", "Список использованных источников", "Источники", "Материалы", "Список литературы"}
NEW_LINE = "\\\\\n"
BLANK_LINE = "\\\\\n~\\\\\n"
BLANK_LINE_LEN = len(BLANK_LINE)
NEW_PAGE = "\n\\newpage\n"
END_DOCUMENT = "\n\\end{document}"
NAME_USELESS_SYMBOLS = {'.', '"', "'", "?"}
SYMBOLS_TO_REPLACE = {
    '"': '"{}',
}
SLASH = "\\"
HLINE = "\\hline"
BEGINS = {"\\begin{enumerate}", "\\begin{itemize}", "\\subsection"}
