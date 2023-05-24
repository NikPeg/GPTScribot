import io

from GPTProxy import GPTProxy
from constants import *
from coursework_messages import *
from utils import log
from transliterate import translit


class CourseWork:
    def __init__(self, name):
        self.name = name
        self.chapters = []
        self.chapters_text = []

    def print(self):
        print(self.text)

    def __str__(self):
        return f"Курсовая работа {self.name}"

    def save(self):
        with io.open(cw.file_name, mode="w", encoding="utf-8") as result_file:
            result_file.write(self.text)

    @property
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

    @property
    def file_name(self):
        translit_name = translit(name, language_code='ru', reversed=True)
        splitted_name = translit_name.split()
        res = ""
        for word in splitted_name:
            res += word
            if len(res) >= 60:
                break
        return f"{res}.tex"


class CourseWorkFactory:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.gpt = GPTProxy(model)

    @staticmethod
    def _strip_chapter(text):
        res = text.strip()
        while res and res[0] in USELESS_SYMBOLS:
            res = res[1:]
        return res.strip()

    def _generate_chapters(self, cw):
        log("Generating chapters...")

        for i in range(10):
            chapters_string = self.gpt.ask(GENERATE_CHAPTERS_LIST.format(cw.name))
            log(f"GPT's response: {chapters_string}")
            chapters_list = chapters_string.split("\n")
            cw.chapters = [self._strip_chapter(chapter) for chapter in chapters_list]
            if len(cw.chapters) >= 5:
                break
        else:
            log(f"!!!There is a problem with {cw.name}!!!")

        if cw.chapters[-1] not in BIBLIOGRAPHIES:
            cw.chapters.append(BIBLIOGRAPHY)
        log(f"Chapters: {cw.chapters}")

    @staticmethod
    def _replace_special_symbols(text, name):
        symbols = BIBLIOGRAPHY_SPECIAL_SYMBOLS if name in BIBLIOGRAPHIES else SPECIAL_SYMBOLS
        res = text
        for c in symbols:
            res = res.replace(c, f"\\{c}")
            res = res.replace(f"\\\\{c}", f"\\{c}")
        for seq in USELESS_SEQUENCES:
            res = res.replace(seq, "")
        return res

    def _validate_chapter(self, text, name):
        res = text
        if SECTION not in text:
            res = f"\n{SECTION}{{{name}}}\n{text}"
        elif not text.startswith(SECTION):
            if name in BIBLIOGRAPHIES:
                res = f"\n{SECTION}*{text.partition(SECTION)[2]}"
            else:
                res = f"\n{SECTION}{text.partition(SECTION)[2]}"
        return self._replace_special_symbols(res, name)

    def _generate_chapters_text(self, cw):
        log("\n\n\nGenerating chapters\' text...")
        for chapter in cw.chapters:
            log(f"\nGenerating chapter {chapter}...")
            chapter_text = self.gpt.ask(GENERATE_CHAPTER.format(chapter, cw.name))
            chapter_text = self._validate_chapter(chapter_text, chapter)
            log(chapter_text)
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
        log(f"Generating coursework {name}...")
        cw = CourseWork(name)
        self._generate_chapters(cw)
        self._generate_chapters_text(cw)
        return cw


if __name__ == "__main__":
    # name = "История программы-примера Hello world и её влияние на мировую культуру"
    name = input(ENTER_NAME)
    factory = CourseWorkFactory()
    cw = factory.generate_coursework(name)
    cw.save()
    log(f"Курсовая работа {name} сгенерирована!")
