from config import OPENAI_API_KEY
import openai
from tenacity import retry, wait_random_exponential, wait_fixed, stop_after_attempt


class GPTProxy:
    def __init__(self, model="gpt-3.5-turbo"):
        openai.api_key = OPENAI_API_KEY
        self.model = model

    @retry(wait=wait_fixed(21), stop=stop_after_attempt(10))
    def ask(self, message):
        try:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": message}
                ]
            )

            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            raise e


def handle_question(question):
    res = ""
    for line in question:
        if line not in {"*", "5 баллов", "10 баллов"}:
            res += line + "\n"
    res += "Choose only one answer"
    return res


if __name__ == "__main__":
    proxy = GPTProxy()
    while True:
        print("\nType your question:")
        line = None
        question = []
        while line != "":
            line = input()
            question.append(line)
        answer = proxy.ask(handle_question(question))
        step = 70
        for i in range(0, len(answer), step):
            print(answer[i:i + step])
