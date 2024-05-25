from openai import OpenAI
import time
from dotenv import load_dotenv

class OpenAIChatClient:
    def __init__(self):
        self.client = OpenAI()
        self.api_key = ['OPENAI_API_KEY']

    def ask(self, prompt,context,model="gpt-3.5-turbo"):
        full_context = context.format(prompt=prompt)  
        stream = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "assistant", "content": full_context},
            ],
            stream=False,
        )
        return stream.choices[0].message.content
    
    def ask_with_data(self, prompt,augmented_data,context,model="gpt-3.5-turbo"):
        full_context = context.format(prompt=prompt,data=augmented_data)  

        stream = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "assistant", "content": full_context},
            ],
            stream=False,
        )
        return stream.choices[0].message.content
        

# [Testing Purpose]
# client = OpenAIChatClient()
# print(client.ask("el precio del trigo en paris durante 2024"))
