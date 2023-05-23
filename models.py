from GPTProxy import GPTProxy
from CourseWorkMessages import *


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
        pass

    @property
    def text(self):
        res = ""
        with open("template.tex", "r") as template:
            res += template.read()
        res += "\\newpage".join(self.chapters_text)
        return res


class CourseWorkFactory:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.gpt = GPTProxy(model)

    def _generate_chapters(self, cw):
        chapters_string = self.gpt.ask(GENERATE_CHAPTERS_LIST.format(cw.name))
        chapters_list = chapters_string.split("- ")[1:]
        cw.chapters = [chapter.strip() for chapter in chapters_list]
        if cw.chapters[-1] not in BIBLIOGRAPHIES:
            cw.chapters.append(BIBLIOGRAPHY)

    def _generate_chapters_text(self, cw):
        for chapter in cw.chapters:
            chapter_text = self.gpt.ask(GENERATE_CHAPTER.format(chapter, cw.name))
            print(chapter_text)
            cw.chapters_text.append(chapter_text)

    def generate_coursework(self, name):
        cw = CourseWork(name)
        self._generate_chapters(cw)
        self._generate_chapters_text(cw)
        return cw


if __name__ == "__main__":
    name = "История программы-примера Hello world и её влияние на мировую культуру"
    factory = CourseWorkFactory()
    cw = factory.generate_coursework(name)
    print("\n\n\nИтоговая работа:")
    print(cw.text)
