from GPTProxy import GPTProxy
from CourseWorkMessages import *


class CourseWork:
    def __init__(self, name, text=""):
        self.name = name
        self.text = text
        self.file_name = f"{name[:60]}.tex"

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

    def _generate_chapters(self, name):
        return self.gpt.ask(GENERATE_CHAPTERS_LIST.format(name))

    def generate_coursework(self, name):
        chapters = self._generate_chapters(name)
        print(chapters)


if __name__ == "__main__":
    name = "История программы-примера Hello world и её влияние на мировую культуру"
    factory = CourseWorkFactory()
    print(factory.generate_coursework(name))
