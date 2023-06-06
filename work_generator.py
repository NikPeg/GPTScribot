import io
import os
import re
from functools import cached_property

from proxy import GPTProxy
from constants import *
from gpt_messages import *
from utils import log
from transliterate import translit
from string import ascii_letters, digits, printable, punctuation
import subprocess


class CourseWork:
    def __init__(self, name, bot=None):
        self.name = name
        self.chapters = []
        self.chapters_text = []
        self.bot = bot

    def print(self):
        print(self.text)

    def __str__(self):
        return f"Курсовая работа {self.name}"

    def save(self) -> bool:
        log("Saving work...", self.bot)
        try:
            with io.open(self.file_name(), mode="w", encoding="utf-8") as result_file:
                result_file.write(self.text)
        except Exception as e:
            log(f"Exception while saving tex: {e}", self.bot)
            return False
        try:
            log("Try to run pdflatex...", self.bot)
            subprocess.run(["pdflatex", self.file_name()], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            result = subprocess.run(["pdflatex", self.file_name()], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            log(result.stdout, bot=self.bot)
            log(result.stderr, bot=self.bot)
            return result.returncode == 0
        except Exception as e:
            log(f"Exception while running pdflatex: {e}", self.bot)
            return False

    @cached_property
    def upper_name(self):
        words_list = self.name.upper().split()[:30]
        words_count = len(words_list)
        res = ""
        if words_count <= 5:
            res += " ".join(words_list)
        elif words_count <= 10:
            res += " ".join(words_list[:words_count // 2]) + NEW_LINE
            res += " ".join(words_list[words_count // 2:]) + NEW_LINE
        else:
            words_count = min(words_count, 15)
            res += " ".join(words_list[:words_count // 3]) + NEW_LINE
            res += " ".join(words_list[words_count // 3:words_count * 2 // 3]) + NEW_LINE
            res += " ".join(words_list[words_count * 2 // 3:words_count]) + NEW_LINE
        return res

    @property
    def text(self):
        res = ""
        for i in range(1, 4):
            with io.open(f"template{i}.tex", mode="r", encoding="utf-8") as template:
                res += template.read()
            if i < 3:
                res += self.upper_name

        res += NEW_PAGE.join(self.chapters_text)
        res += END_DOCUMENT
        return res

    def file_name(self, type="tex"):
        translit_name = translit(self.name, language_code='ru', reversed=True)
        splitted_name = translit_name.split()
        res = ""
        for word in splitted_name:
            res += " " + word if res else word
            if len(res) >= 60:
                break
        ascii_res = ""
        for c in res:
            if c in ascii_letters + digits + " \t\n":
                ascii_res += c
        return f"{ascii_res}.{type}"

    def delete(self, delete_tex: bool = True):
        for file_type in "aux", "log", "pdf", "toc":
            try:
                os.remove(self.file_name(file_type))
            except:
                pass
        if delete_tex:
            try:
                os.remove(self.file_name("tex"))
            except:
                pass


class CourseWorkFactory:
    def __init__(self, model="gpt-3.5-turbo", bot=None):
        self.model = model
        self.gpt = GPTProxy(model)
        self.ref_index = 1
        self.cite_index = 1
        self.bot = bot

    @staticmethod
    def _strip_chapter(text):
        res = text.strip()
        while res and res[0] in USELESS_SYMBOLS:
            res = res[1:]
        while res and res[-1] in USELESS_SYMBOLS:
            res = res[:-1]
        return res.strip()

    def _generate_chapters(self, cw):
        log("Generating chapters...", self.bot)

        for i in range(10):
            cw.chapters = []
            chapters_string = self.gpt.ask(GENERATE_CHAPTERS_LIST.format(cw.name))
            log(f"GPT's response: {chapters_string}", self.bot)
            chapters_list = chapters_string.split("\n")
            for chapter in chapters_list:
                chapter_name = self._strip_chapter(chapter)
                if chapter_name:
                    cw.chapters.append(chapter_name)
            if len(cw.chapters) >= 5:
                break
        else:
            log(f"!!!There is a problem with {cw.name}!!!", self.bot)

        if cw.chapters[-1] not in BIBLIOGRAPHIES:
            cw.chapters.append(BIBLIOGRAPHY)
        # cw.chapters.append("Введение")
        log(f"Chapters: {cw.chapters}", self.bot)

    def _next_bibitem(self, match):
        result = f'\\bibitem{{ref{self.ref_index}}}'
        self.ref_index += 1
        return result

    def _next_cite(self, match):
        result = f'\\cite{{ref{self.cite_index}}}'
        self.cite_index += 1
        return result

    def _replace_special_symbols(self, text, name):
        symbols = BIBLIOGRAPHY_SPECIAL_SYMBOLS if name in BIBLIOGRAPHIES else SPECIAL_SYMBOLS
        res = ""
        for c in text:
            if c in digits + ascii_letters + punctuation + RUSSIAN + " \n":
                res += c
        for c in symbols:
            res = res.replace(c, f"\\{c}")
            res = res.replace(f"\\\\{c}", f"\\{c}")
        for c in SYMBOLS_TO_REPLACE:
            res = res.replace(c, SYMBOLS_TO_REPLACE[c])
        for seq in USELESS_SEQUENCES:
            res = res.replace(seq, "")
        if name in BIBLIOGRAPHIES:
            self.ref_index = 1
            res = re.sub(r'\\bibitem\{.*?\}', self._next_bibitem, res)
        else:
            self.cite_index = 1
            res = re.sub(r'\\cite\{.*?\}', self._next_cite, res)
            res = re.sub(r"\$(?=\d)", r"\\$", res)
        return res

    @staticmethod
    def _add_section(text, name, section):
        try:
            new_line_index = text.index("\n")
            first_line = text[:new_line_index]
            if name in first_line or first_line.startswith(RUSSIAN_SECTION):
                return f"\n{section}{{{name}}}\n{text[new_line_index + 2:]}"
            else:
                return f"\n{section}{{{name}}}\n{text}"
        except ValueError:
            return f"\n{section}{{{name}}}\n{text}"

    @staticmethod
    def _reorder_section(text, section):
        return f"\n{section}{text.partition(SECTION)[2]}"

    def _validate_chapter(self, text, name):
        res = text
        if name in BIBLIOGRAPHIES:
            section = BIBLIOGRAPHY_SECTION
        else:
            section = SECTION
        if SECTION not in text:
            res = self._add_section(text, name, section)
        elif not text.startswith(SECTION):
            res = self._reorder_section(text, section)
        return self._replace_special_symbols(res, name)

    @staticmethod
    def _delete_blank_line(text):
        if text.endswith(BLANK_LINE):
            return f"{text[:-BLANK_LINE_LEN]}\n"
        return text

    @staticmethod
    def _chapter_with_blank_lines(text):
        res = ""
        for line in text.split("\n"):
            line = line.strip()
            for begin in BEGINS_WITHOUT_NEW_LINES:
                if line.startswith(begin):
                    res = CourseWorkFactory._delete_blank_line(res)
            if line:
                for end in ENDS_WITHOUT_NEW_LINES:
                    if line.endswith(end):
                        res += f"{line}\n"
                        break
                else:
                    res += f"{line}{BLANK_LINE}"
        return res

    def _generate_chapters_text(self, cw):
        log("\n\n\nGenerating chapters\' text...", self.bot)
        for chapter in cw.chapters:
            log(f"\nGenerating chapter {chapter}...", self.bot)
            if chapter in BIBLIOGRAPHIES:
                chapter_text = self.gpt.ask(GENERATE_BIBLIOGRAPHY.format(cw.name))
            else:
                chapter_text = self.gpt.ask(GENERATE_CHAPTER.format(chapter, cw.name))
            log(f"GPT's response: {chapter_text}", self.bot)
            chapter_text = self._validate_chapter(chapter_text, chapter)
            if chapter not in BIBLIOGRAPHIES:
                chapter_text = self._chapter_with_blank_lines(chapter_text)
            log(chapter_text, self.bot)
            cw.chapters_text.append(chapter_text)

    @staticmethod
    def _strip_name(name):
        res = name
        while res and res[0] in NAME_USELESS_SYMBOLS:
            res = res[1:]
        while res and res[-1] in NAME_USELESS_SYMBOLS:
            res = res[:-1]
        return res.strip()

    def generate_coursework(self, name):
        name = self._strip_name(name)
        log(f"Generating coursework {name}...", self.bot)
        cw = CourseWork(name, bot=self.bot)
        if os.path.exists(cw.file_name()):
            log("The file is already exist!", self.bot)
            return cw
        self._generate_chapters(cw)
        self._generate_chapters_text(cw)
        return cw


if __name__ == "__main__":
    # name = "История программы-примера Hello world и её влияние на мировую культуру"
    name = input(ENTER_NAME)
    factory = CourseWorkFactory()
    cw = factory.generate_coursework(name)
    cw.save()
    log(f"Курсовая работа\n{cw.name} сгенерирована!")
