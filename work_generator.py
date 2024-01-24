import enum
import io
import os
import random
import re
import string
from functools import cached_property

import config
from proxy import GPTProxy
from constants import *
from gpt_messages import *
from utils import log
from transliterate import translit
from string import ascii_letters, digits, printable, punctuation
import subprocess
from google_images_search import GoogleImagesSearch
import shutil


class CourseWorkType(enum.StrEnum):
    DIPLOMA = "Дипломная работа"
    COURSE_WORK = "Курсовая работа"


class CourseWork:
    def __init__(self, name, bot=None, work_type=CourseWorkType.COURSE_WORK, additional_sections=""):
        self.name = name
        self.chapters = []
        self.chapters_text = []
        self.bot = bot
        self.work_type = work_type
        self.additional_sections = additional_sections

    def print(self):
        print(self.text)

    def __str__(self):
        return f"Курсовая работа {self.name}"

    def save(self, free=True) -> bool:
        log("Saving work...", self.bot)
        try:
            with io.open(self.file_name(), mode="w", encoding="utf-8") as result_file:
                result_file.write(self.text(free))
            self.bot.send_document(config.ADMIN, open(self.file_name("tex"), 'rb'))
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

    def text(self, free=True):
        res = ""
        for i in range(1, 4):
            with io.open(f"template{i}.tex", mode="r", encoding="utf-8") as template:
                res += template.read()
            if i < 3:
                res += f"{self.upper_name}{BIG_INDENT}{self.work_type}{NEW_LINE}"
        with io.open(f"templateFree.tex", mode="r", encoding="utf-8") as template:
            free_text = template.read().format(price=config.PRICE)
        if free:
            for chapter in self.chapters_text[:len(self.chapters) // 2]:
                res += NEW_PAGE + chapter
            for chapter_name in self.chapters[len(self.chapters) // 2:]:
                res += NEW_PAGE
                if chapter_name in BIBLIOGRAPHIES:
                    section = BIBLIOGRAPHY_SECTION
                else:
                    section = SECTION
                res += f"\n{section}{{{chapter_name}}}\n{free_text}"
        else:
            res += NEW_PAGE.join(self.chapters_text)
        res += END_DOCUMENT
        return res

    def file_name(self, type="tex"):
        translit_name = translit(self.name, language_code='ru', reversed=True)
        ascii_name = ""
        for c in translit_name:
            if c in ascii_letters + digits + " ":
                ascii_name += c
        splitted_name = ascii_name.split()
        res = ""
        for word in splitted_name:
            res += " " + word if res else word
            if len(res) >= 60:
                break
        return f"{res}.{type}"

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
        self.gis = GoogleImagesSearch(config.GOOGLE_DEVELOPER_KEY, config.GOOGLE_CUSTOM_SEARCH_CX)

    @staticmethod
    def _strip_chapter(text):
        res = text.strip()
        if USELESS_SUBSTRING in res.lower():
            return None
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
            if cw.additional_sections:
                log("Ask GPT to add sections...", self.bot)
                chapters_string = self.gpt.ask(ADD_SECTIONS.format(chapters_string, cw.additional_sections))
                log(f"GPT's response: {chapters_string}", self.bot)
            chapters_list = chapters_string.split("\n")
            for chapter in chapters_list:
                chapter_name = self._strip_chapter(chapter)
                if chapter_name:
                    cw.chapters.append(chapter_name)
            if len(cw.chapters) >= 7:
                break
        else:
            log(f"!!!There is a problem with {cw.name}!!!", self.bot)

        if cw.chapters[-1] not in BIBLIOGRAPHIES and cw.chapters[-2] not in BIBLIOGRAPHIES:
            cw.chapters.append(BIBLIOGRAPHY)
        log(f"Chapters: {cw.chapters}", self.bot)

    def _generate_subchapters(self, subchapter, cw):
        log("Generating subchapters...", self.bot)

        subchapters = []
        subchapters_string = self.gpt.ask(GENERATE_SUBCHAPTERS_LIST.format(subchapter, cw.name))
        log(f"GPT's response: {subchapters_string}", self.bot)
        subchapters_list = subchapters_string.split("\n")
        for subchapter in subchapters_list:
            subchapter_name = self._strip_chapter(subchapter)
            if subchapter_name:
                subchapters.append(subchapter_name)
        log(f"Subchapters: {subchapters}", self.bot)
        return subchapters

    def _next_bibitem(self, match):
        result = f'\\bibitem{{ref{self.ref_index}}}'
        self.ref_index += 1
        return result

    def _next_cite(self, match):
        result = f'\\cite{{ref{self.cite_index}}}'
        self.cite_index += 1
        return result

    def _ask_to_replace(self, match):
        symbol = match.re.pattern
        s = match.string
        if match.span()[0] == len(s):
            return ""
        log(f"Asking GPT about symbol {symbol}", self.bot)
        log(f"Len of string: {len(s)}, symbol index: {match.span()[0]}", self.bot)
        substring = s[max(0, match.span()[0] - 100):min(len(s), match.span()[0] + 100)]
        log(f"Substring to ask: {substring}", self.bot)
        gpt_answer = self.gpt.ask(SYMBOLS_TO_ASK[symbol].format(substring))
        log(f"GPT's answer: {gpt_answer}", self.bot)
        if gpt_answer.lower().startswith('нет'):
            return f"\\{symbol}"
        else:
            return symbol

    def _replace_ampersand(self, text):
        opened_table = False
        i = 0
        while i < len(text):
            if text[i:i + len(TABLE_OPEN_SUBSTRING)] == TABLE_OPEN_SUBSTRING:
                opened_table = True
                i += len(TABLE_OPEN_SUBSTRING)
                log(f"Fount table in position {i}", self.bot)
            elif text[i:i + len(TABLE_CLOSE_SUBSTRING)] == TABLE_CLOSE_SUBSTRING:
                opened_table = False
                i += len(TABLE_CLOSE_SUBSTRING)
                log(f"Table closed in position {i}", self.bot)
            elif text[i] == "&" and not opened_table and (i == 0 or text[i - 1] != "\\"):
                log(f"Fount & in position {i} not in table", self.bot)
                text = text[:i] + "\\" + text[i:]
                i += 3
            else:
                i += 1
        return text.replace("\\\\&", "\\&")

    def _replace_special_symbols(self, text, name, work_type):
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
            res = res.replace(f"\\\\{c}", f"\\{c}")
        for c in SYMBOLS_TO_ASK:
            res = re.sub(c, self._ask_to_replace, res)
            res = res.replace(f"\\\\{c}", f"\\{c}")
        for seq in USELESS_SEQUENCES:
            res = res.replace(seq, "")
            res = res.replace(seq, "")
        res = self._replace_ampersand(res)
        if name in BIBLIOGRAPHIES:
            self.ref_index = 1
            res = re.sub(r'\\bibitem\{.*?\}', self._next_bibitem, res)
        else:
            self.cite_index = 1
            res = re.sub(r'\\cite\{.*?\}', self._next_cite, res)
        if work_type == CourseWorkType.COURSE_WORK:
            res = res.replace("дипломн", "курсов")
            res = res.replace("Дипломн", "Курсов")
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

    def _validate_chapter(self, text, name, work_type):
        res = text
        if name in BIBLIOGRAPHIES:
            section = BIBLIOGRAPHY_SECTION
        else:
            section = SECTION
        if SECTION not in text:
            res = self._add_section(text, name, section)
        elif not text.startswith(SECTION):
            res = self._reorder_section(text, section)
        return self._replace_special_symbols(res, name, work_type)

    def _validate_subchapter(self, text, name, work_type):
        res = text
        section = SUBSECTION
        if SECTION not in text:
            res = self._add_section(text, name, section)
        elif not text.startswith(SECTION):
            res = self._reorder_section(text, section)
        return self._replace_special_symbols(res, name, work_type)

    def _add_photos(self, text):
        photo_index = 0
        while photo_index < len(text):
            photo_index = text.find(PICTURE_SUBSTRING, photo_index)
            if photo_index == -1:
                break
            log(f"Photo index: {photo_index}", self.bot)
            filename_match = re.compile(r'\\includegraphics.*\{(.+?)\..*\}').search(text[photo_index:])
            full_filename_match = re.compile(r'\\includegraphics.*\{(.+?)\}').search(text[photo_index:])
            description_match = re.compile(r'\\caption\{(.+?)\}').search(text[photo_index:])
            if filename_match and full_filename_match and description_match:
                filename = filename_match.group(1)
                full_filename = full_filename_match.group(1)
                description = description_match.group(1)
                new_filename = f"{filename}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}"
                log(
                    f"Filename: {filename}, full filename: {full_filename}, new filename: {new_filename}, "
                    f"description: {description}",
                    self.bot
                )
                _search_params = {
                    "q": description,
                    "fileType": "png",
                    "num": 1
                }
                try:
                    self.gis.search(search_params=_search_params, path_to_dir='pictures/', custom_image_name=new_filename)
                    text = text.replace(full_filename, new_filename)
                except Exception as e:
                    log(f"Exception while loading picture: {e}", self.bot)
                    files = os.listdir("pictures/")
                    text = text.replace(full_filename, random.choice(files))
            else:
                log(f"Problem with picture {text[photo_index:photo_index + 200]}", self.bot)
            photo_index += len(PICTURE_SUBSTRING)
        return text

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
                chapter_text = f"\n{SECTION}{{{chapter}}}\n"
                for subchapter in self._generate_subchapters(chapter, cw):
                    log(f"Asking GPT about subchapter's {subchapter} text...", self.bot)
                    subchapter_text = self.gpt.ask(GENERATE_SUBCHAPTER.format(subchapter, cw.name))
                    subchapter_text = self._validate_subchapter(subchapter_text, subchapter, cw.work_type)
                    log(f"Subchapter's text: {subchapter_text}", self.bot)
                    chapter_text += subchapter_text
            log(f"Chapter's text: {chapter_text}", self.bot)
            chapter_text = self._validate_chapter(chapter_text, chapter, cw.work_type)
            chapter_text = self._add_photos(chapter_text)
            if chapter not in BIBLIOGRAPHIES:
                chapter_text = self._chapter_with_blank_lines(chapter_text)
            log(chapter_text, self.bot)
            cw.chapters_text.append(chapter_text)

    def _process_name(self, name):
        res = name
        additional_sections = ""
        log("Asking GPT about additional topics...", self.bot)
        if self.gpt.ask(SECTIONS_QUESTION.format(res)).lower().startswith("да"):
            log("Asking GPT about additional topics list...", self.bot)
            additional_sections = self.gpt.ask(SECTIONS_LIST_QUESTION.format(res))
            log(f"Additional topics list: {additional_sections}", self.bot)
        log(f"Asking GPT about name...", self.bot)
        gpt_work_name = self.gpt.ask(WORK_NAME.format(res))
        log(f"GPT's answer: {gpt_work_name}", self.bot)
        if REGRET_SUBSTRING not in gpt_work_name:
            res = gpt_work_name
        if res.startswith(USELESS_START_STRING):
            res = res[len(USELESS_START_STRING):]
        while res and res[0] in NAME_USELESS_SYMBOLS:
            res = res[1:]
        while res and res[-1] in NAME_USELESS_SYMBOLS:
            res = res[:-1]
        res = res.strip()
        return res, additional_sections

    def generate_coursework(self, name):
        work_type = CourseWorkType.DIPLOMA if DIPLOMA_SUBSTRING in name else CourseWorkType.COURSE_WORK
        name, additional_sections = self._process_name(name)
        log(f"Generating coursework {name}...", self.bot)
        cw = CourseWork(name, bot=self.bot, work_type=work_type, additional_sections=additional_sections)
        if os.path.exists(cw.file_name()):
            log("The file is already exist!", self.bot)
            cw.delete()
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
