import enum
import io
import os
import random
import re
import string
import subprocess
from functools import cached_property
from string import ascii_letters, digits, punctuation
from pdf2docx import Converter
import qr_gen

from google_images_search import GoogleImagesSearch
from transliterate import translit

import config
import constants
from bot_api import edit_status_message
from constants import *
from gpt_messages import *
from proxy import GPTProxy
from cloudpayments import CloudPayments
from mongo_utils import DBClient
CP = CloudPayments(config.PAYMENTS_ID, config.PAYMENTS_TOKEN)
DB = DBClient(config.MONGO_CLIENT_REF, config.DB_NAME)



class WorkType(enum.Enum):
    DIPLOMA = "Дипломная работа"
    COURSE_WORK = "Курсовая работа"
    REFERENCE = "Реферат"
    REPORT = "Доклад"
    RESEARCH = "Исследовательская работа"
    PRACTICE = "Отчет по практике"

    @staticmethod
    def from_name(name):
        match name:
            case "diploma":
                return WorkType.DIPLOMA
            case "coursework":
                return WorkType.COURSE_WORK
            case "reference":
                return WorkType.REFERENCE
            case "report":
                return WorkType.REPORT
            case "research":
                return WorkType.RESEARCH
            case "practice":
                return WorkType.PRACTICE

    @property
    def substring(self):
        match self:
            case WorkType.DIPLOMA:
                return "дипломной работы"
            case WorkType.COURSE_WORK:
                return "курсовой работы"
            case WorkType.REFERENCE:
                return "реферата"
            case WorkType.REPORT:
                return "доклада"
            case WorkType.RESEARCH:
                return "исследовательской работы"
            case WorkType.PRACTICE:
                return "отчета по практике"


SYMBOLS_IN_PAGE = 2100


class CourseWork:
    def __init__(self, name, DB, CP, bot=None, work_type=WorkType.COURSE_WORK, additional_sections=""):
        self.name = name
        self.chapters = []
        self.chapters_text = []
        self.bot = bot
        self.work_type = work_type
        self.additional_sections = additional_sections
        self.size = 20
        self.symbols_in_chapter = None
        self.DB = DB
        self.CP =CP
        

    def print(self):
        print(self.text)

    def __str__(self):
        return f"Курсовая работа {self.name}"
          
    def save(self, user_id, free=True) -> bool:
        print("Saving work...", self.bot)
        old_data = self.DB.find(config.COLLECTION_NAME, False, {"tg_id":user_id}) 

        order = self.CP.create_order(amount=int(config.PRICE), description= f"Оплата работы by NikPeg пользователем https://t.me/{user_id} \n рекомендуем указывать вашу почту.", currency="RUB" )             
        self.DB.update(config.COLLECTION_NAME, {"tg_id":user_id, "order_data":old_data["order_data"]}, { "$set": { "order_data":{"payment_link":order.url, "number":order.number}}}, True)
        qr_gen.create_link(url=order.url)
        print("work_gen str 96 user_id:",user_id)
        try:
            with io.open(self.file_name(), mode="w", encoding="utf-8") as result_file:
                result_file.write(self.text(free, url=order.url))
            if self.bot:
                self.bot.send_document(config.ADMIN, open(self.file_name("tex"), 'rb'))
        except Exception as e:
            print(f"Exception while saving tex: {e}")
            return False

        print("Starting pdflatex...", self.bot)
        try:
            subprocess.run(["pdflatex", self.file_name()], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            print(f"Exception while running pdflatex: {e}", self.bot)
        try:
            result = subprocess.run(["pdflatex", self.file_name()], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result.stderr, self.bot)
        except Exception as e:
            print(f"Second exception while running pdflatex: {e}", self.bot)

        if not os.path.isfile(self.file_name("pdf")):
            print(f"No pdf file fount: {self.file_name('pdf')}", self.bot)
            return False

        try:
            print("Converting pdf to docx...", self.bot)
            cv = Converter(self.file_name("pdf"))
            cv.convert(self.file_name("docx"), start=0, end=None)
            cv.close()
        except Exception as e:
           print(f"Exception while converting pdf to docx: {e}", self.bot)

        return True

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
      
    def text(self, free=True, url="url"): ###
        res = ""
        for i in range(2, 4):
            with io.open(f"template{i}.tex", mode="r", encoding="utf-8") as template:
                res += template.read()
            if i < 3:
                res += f"{self.upper_name}{BIG_INDENT}{self.work_type.value}{NEW_LINE}"
        with io.open(f"templateFree.tex", mode="r", encoding="utf-8") as template:
            free_text = template.read().format(link=url, price=config.PRICE)
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
        for file_type in constants.ALL_FILE_TYPES:
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
    def __init__(self, DB, CP, model="gpt-3.5-turbo", bot=None):
        self.model = model
        self.gpt = GPTProxy(model)
        self.ref_index = 1
        self.cite_index = 1
        self.bot = bot
        self.gis = GoogleImagesSearch(config.GOOGLE_DEVELOPER_KEY, config.GOOGLE_CUSTOM_SEARCH_CX)
        self.DB = DB
        self.CP =CP

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
        print("Generating chapters...", self.bot)
        cw.chapters = []
        for i in range(config.TRIES_COUNT):
            chapters = []
            chapters_string = self.gpt.ask(
                GENERATE_CHAPTERS_LIST.format(cw.name, cw.work_type.substring, cw.size // 3)
            )
            print(f"GPT's response: {chapters_string}", self.bot)
            if cw.additional_sections:
                print("Ask GPT to add sections...", self.bot)
                chapters_string = self.gpt.ask(
                    ADD_SECTIONS.format(chapters_string, cw.additional_sections, cw.work_type.substring))
                print(f"GPT's response: {chapters_string}", self.bot)
            chapters_list = chapters_string.split("\n")
            for chapter in chapters_list:
                chapter_name = self._strip_chapter(chapter)
                if chapter_name:
                    chapters.append(chapter_name)
            if len(chapters) >= len(cw.chapters):
                cw.chapters = chapters
        cw.chapters = cw.chapters[:cw.size // 2]
        if cw.chapters[-1] not in BIBLIOGRAPHIES and cw.chapters[-2] not in BIBLIOGRAPHIES:
            cw.chapters.append(BIBLIOGRAPHY)
        print(f"Chapters: {cw.chapters}", self.bot)
        cw.symbols_in_chapter = cw.size * SYMBOLS_IN_PAGE // len(cw.chapters)
        print("Symbols in chapter: ", cw.symbols_in_chapter)

    def _generate_subchapters(self, chapter, cw):
        print("Generating subchapters...", self.bot)

        subchapters = []
        subchapters_string = self.gpt.ask(
            GENERATE_SUBCHAPTERS_LIST.format(chapter, cw.name, cw.work_type.substring))
        print(f"GPT's response: {subchapters_string}", self.bot)
        subchapters_list = subchapters_string.split("\n")
        for subchapter in subchapters_list:
            subchapter_name = self._strip_chapter(subchapter)
            if subchapter_name and subchapter_name.lower() != INTRODUCTION:
                subchapters.append(subchapter_name)
        print(f"Subchapters: {subchapters}", self.bot)
        return subchapters

    def _next_bibitem(self, match):
        result = f'\\bibitem{{ref{self.ref_index}}}'
        self.ref_index += 1
        return result

    def _next_cite(self, match):
        result = f'\\cite{{ref{self.cite_index}}}'
        self.cite_index += 1
        return result

    def _replace_ampersand(self, text):
        opened_table = False
        i = 0
        while i < len(text):
            if text[i:i + len(TABLE_OPEN_SUBSTRING)] == TABLE_OPEN_SUBSTRING:
                opened_table = True
                i += len(TABLE_OPEN_SUBSTRING)
                print(f"Fount table in position {i}", self.bot)
            elif text[i:i + len(TABLE_CLOSE_SUBSTRING)] == TABLE_CLOSE_SUBSTRING:
                opened_table = False
                i += len(TABLE_CLOSE_SUBSTRING)
                print(f"Table closed in position {i}", self.bot)
            elif text[i] == "&" and not opened_table and (i == 0 or text[i - 1] != "\\"):
                print(f"Fount & in position {i} not in table", self.bot)
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
        for c in SYMBOLS_TO_ESCAPE:
            res = res.replace(f"\\\\{c}", f"{c}")
            res = res.replace(f"\\{c}", f"{c}")
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
        return f"\n{section}{text.partition(section)[2]}"

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
        if section not in text:
            res = self._add_section(text, name, section)
        elif not text.startswith(section):
            res = self._reorder_section(text, section)
        return self._replace_special_symbols(res, name, work_type)

    def _add_photos(self, text):
        photo_index = 0
        while photo_index < len(text):
            photo_index = text.find(PICTURE_SUBSTRING, photo_index)
            if photo_index == -1:
                break
            print(f"Photo index: {photo_index}", self.bot)
            filename_match = re.compile(r'\\includegraphics.*\{(.+?)\..*\}').search(text[photo_index:])
            full_filename_match = re.compile(r'\\includegraphics.*\{(.+?)\}').search(text[photo_index:])
            description_match = re.compile(r'\\caption\{(.+?)\}').search(text[photo_index:])
            if filename_match and full_filename_match and description_match:
                filename = filename_match.group(1)
                full_filename = full_filename_match.group(1)
                description = description_match.group(1)
                new_filename = f"{filename}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}"
                print(
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
                    self.gis.search(search_params=_search_params, path_to_dir='pictures/',
                                    custom_image_name=new_filename)
                    text = text.replace(full_filename, new_filename)
                except Exception as e:
                    print(f"Exception while loading picture: {e}", self.bot)
                    files = os.listdir("pictures/")
                    text = text.replace(full_filename, random.choice(files))
            else:
                print(f"Problem with picture {text[photo_index:photo_index + 200]}", self.bot)
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

    def _generate_chapters_text(self, cw, status_message):
        print("\n\n\nGenerating chapters\' text...", self.bot)
        for i, chapter in enumerate(cw.chapters, 1):
            print(f"\nGenerating chapter {chapter}...", self.bot)
            if chapter in BIBLIOGRAPHIES:
                ask_string = GENERATE_BIBLIOGRAPHY.format(cw.name, cw.work_type.substring) + BIBLIOGRAPHY_PREFIX
                print("Asking GPT: " + ask_string, self.bot)
                chapter_text = BIBLIOGRAPHY_PREFIX + self.gpt.ask(ask_string)
                if BIBLIOGRAPHY_POSTFIX not in chapter_text:
                    chapter_text += BIBLIOGRAPHY_POSTFIX + "\\\\\n"
                print("GPT answer: " + chapter_text, self.bot)
            else:
                chapter_text = self.gpt.ask(
                    GENERATE_CHAPTER.format(chapter, cw.name, cw.work_type.substring)
                ) + "\n"
                if len(chapter_text) < cw.symbols_in_chapter:
                    for subchapter in self._generate_subchapters(chapter, cw):
                        print(f"Asking GPT about subchapter's {subchapter} text...", self.bot)
                        subchapter_text = self.gpt.ask(
                            GENERATE_SUBCHAPTER.format(subchapter, chapter, cw.name, cw.work_type.substring))
                        subchapter_text = self._validate_subchapter(subchapter_text, subchapter, cw.work_type)
                        chapter_text += subchapter_text + "\n"
                        if len(chapter_text) > cw.symbols_in_chapter:
                            break
            chapter_text = self._validate_chapter(chapter_text, chapter, cw.work_type)
            chapter_text = self._add_photos(chapter_text)
            if chapter not in BIBLIOGRAPHIES:
                chapter_text = self._chapter_with_blank_lines(chapter_text)
            print(chapter_text, self.bot)
            cw.chapters_text.append(chapter_text)
            edit_status_message(status_message, self.bot, i, len(cw.chapters))

    def _process_name(self, cw: CourseWork):
        res = cw.name
        additional_sections = ""
        print("Asking GPT about additional topics...", self.bot)
        if self.gpt.ask(SECTIONS_QUESTION.format(res)).lower().startswith("да"):
            print("Asking GPT about additional topics list...", self.bot)
            additional_sections = self.gpt.ask(SECTIONS_LIST_QUESTION.format(res))
            print(f"Additional topics list: {additional_sections}", self.bot)
        for useless_string in USELESS_START_STRINGS:
            if res.startswith(useless_string):
                res = res[len(useless_string):]
        while res and res[0] in NAME_USELESS_SYMBOLS:
            res = res[1:]
        while res and res[-1] in NAME_USELESS_SYMBOLS:
            res = res[:-1]
        res = res.strip()
        return res, additional_sections

    def create_coursework(self, name):
        return CourseWork(name, bot=self.bot, DB=self.DB, CP=self.CP)

    def generate_coursework(self, cw, status_message):
        cw.name, cw.additional_sections = self._process_name(cw)
        print(f"Generating {cw.work_type.value} {cw.name} with size {cw.size}...", self.bot)
        if os.path.exists(cw.file_name()):
            print("The file is already exist!", self.bot)
            cw.delete()
        self._generate_chapters(cw)
        self._generate_chapters_text(cw, status_message)
        return cw



if __name__ == "main":
    name = "История программы-примера Hello world и её влияние на мировую культуру"
        #name = input(ENTER_NAME)
    factory = CourseWorkFactory()
    cw = CourseWork(name)
    cw = factory.generate_coursework(cw, None)
    cw.save(1264861053)
    print(f"Курсовая работа\n{cw.name} сгенерирована!")
