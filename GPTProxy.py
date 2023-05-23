from config import OPENAI_API_KEY
import openai
from tenacity import retry, wait_random_exponential


class GPTProxy:
    def __init__(self, model="gpt-3.5-turbo"):
        openai.api_key = OPENAI_API_KEY
        self.model = model

    @retry(wait=wait_random_exponential(multiplier=1, max=60))
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


if __name__ == "__main__":
    proxy = GPTProxy()
    print(proxy.ask("How do you do?"))
