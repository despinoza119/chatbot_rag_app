from openai import OpenAI
import time
from dotenv import load_dotenv
from prompts import PROMPT_ABASTORES

class OpenAIChatClient:
    def __init__(self):
        self.client = OpenAI()
        self.api_key = ['OPENAI_API_KEY']

    def ask(self, prompt,model="gpt-3.5-turbo"):
        stream = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "assistant", "content": PROMPT_ABASTORES},
                {"role": "system", "content": f'La pregunta a responder es la siguiente: {prompt}".'},
            ],
            stream=False,
        )
        return stream.choices[0].message.content
    

# [Testing Purpose]
client = OpenAIChatClient()
print(client.ask("el precio del trigo en paris durante 2024"))
