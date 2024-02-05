import os
from dotenv import load_dotenv

_ = load_dotenv('config.env')

MODEL = os.environ['OLLAMA_MODEL']
ENDPOINT = os.environ['OLLAMA_ENDPOINT']
sentence_endings = [".", "!", "?", ":", "。", "！", "？", "："]

import asyncio
from ollama import AsyncClient

# create a Chat Class
# create a method called chat
# create a method called get_response

class OllamaChat:
    def __init__(self, model = MODEL, endpoint = ENDPOINT):
        self.model = model
        self.endpoint = endpoint
        self.staging = [""]
        self. response = [""]
        self.client = AsyncClient(host = self.endpoint)

    async def chat(self, prompt: str = "Hello, how may I assist you?", callback = None):
        message = {
        'role': 'user', 
        'content': "This is a chat history between user and AI. You are AI. Chat in a very human way, limit to 50 tokens: " + prompt
        }
        try:
            async for part in await self.client.chat(model=self.model, 
                                                    messages=[message], stream=True):
                received = part['message']['content']
                self.staging.append(received)
                staged = ''.join(self.staging)
                # if staged contains any comma, period, exclaimation mark, question mark, or colon, it is a complete sentence
                # pop the last recognition from self.staging and append it to self.response
                if staged != "" and any([c in staged for c in sentence_endings]):
                    self.response.append(staged)
                    self.staging = [""]
                    if callback:
                        await callback(staged)
        except Exception as e:
            print(e)
            


# test the OllamaChat class
def test_ollama_chat():
    ollama = OllamaChat()
    async def test_callback(staged):
        print(staged)
    asyncio.run(ollama.chat("Hello, how may I assist you?", callback=test_callback))

