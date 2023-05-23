from functools import cached_property

from GPTProxy import GPTProxy
from CourseWorkMessages import *
from utils import log
import io
from tenacity import retry, wait_random_exponential


class CourseWork:
    def __init__(self, name):
        self.name = name
        self.file_name = f"{name[:60]}.tex"
        self.chapters = []
        self.chapters_text = []

    def print(self):
        print(self.text)

    def __str__(self):
        return f"Курсовая работа {self.name}"

    def save(self):
        with io.open(f"{cw.file_name}.tex", mode="w", encoding="utf-8") as result_file:
            result_file.write(self.text)

    @cached_property
    def text(self):
        res = ""
        with io.open("template.tex", mode="r", encoding="utf-8") as template:
            res += template.read()
        res += "\\newpage".join(self.chapters_text)
        return res


class CourseWorkFactory:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.gpt = GPTProxy(model)

    def _generate_chapters(self, cw):
        log("Generating chapters...")
        for i in range(10):
            chapters_string = self.gpt.ask(GENERATE_CHAPTERS_LIST.format(cw.name))
            log(f"GPT's response: {chapters_string}")
            chapters_list = chapters_string.split("- ")[1:]
            cw.chapters = [chapter.strip() for chapter in chapters_list]
            if len(cw.chapters) >= 5:
                break
        else:
            log(f"!!!There is a problem with {cw.name}!!!")
        if cw.chapters[-1] not in BIBLIOGRAPHIES:
            cw.chapters.append(BIBLIOGRAPHY)
        log(f"Chapters: {cw.chapters}")

    def _generate_chapters_text(self, cw):
        log("Generating chapters\' text...")
        for chapter in cw.chapters:
            log(f"\n\n\nGenerating chapter {chapter}...")
            chapter_text = self.gpt.ask(GENERATE_CHAPTER.format(chapter, cw.name))
            log(chapter_text)
            cw.chapters_text.append(chapter_text)

    def generate_coursework(self, name):
        log(f"Generating coursework {name}...")
        cw = CourseWork(name)
        self._generate_chapters(cw)
        self._generate_chapters_text(cw)
        return cw


if __name__ == "__main__":
    name = "История программы-примера Hello world и её влияние на мировую культуру"
    factory = CourseWorkFactory()
    cw = factory.generate_coursework(name)
    cw.save()
