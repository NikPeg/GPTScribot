from GPTProxy import GPTProxy
from CourseWorkMessages import *


class CourseWork:
    def __init__(self, name, text=""):
        self.name = name
        self.text = text
        self.file_name = f"{name[:60]}.tex"
        self.chapters = []

    def print(self):
        print(self.text)

    def __str__(self):
        return f"Курсовая работа {self.name}"

    def save(self):
        pass


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

    def generate_coursework(self, name):
        cw = CourseWork(name)
        self._generate_chapters(cw)
        return cw


if __name__ == "__main__":
    name = "История программы-примера Hello world и её влияние на мировую культуру"
    factory = CourseWorkFactory()
    cw = factory.generate_coursework(name)
    print(cw.chapters)
