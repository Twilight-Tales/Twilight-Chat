import os
from dotenv import load_dotenv
from openai import OpenAI

_ = load_dotenv('config.env')

# Set API keys
openAIClient = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

MODEL_ENGINE = "gpt-3.5-turbo"
sentence_endings = [".", "!", "?", ":", "。", "！", "？", "："]

class OpenAIChat:
    def __init__(self, model = MODEL_ENGINE):
        self.model = model
        self.staging = [""]

    async def chat(self, prompt: str = "Hello, how may I assist you?", callback = None):
        response = openAIClient.chat.completions.create(
            model=MODEL_ENGINE,
            messages=[
                {
                    "role": "user",
                    "content": "This is a chat history between user and AI. You are AI. Chat in a very human way, limit to 50 tokens: " + prompt
                },
            ],
            max_tokens=50,
            stream=True # stream the response
        )

        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            if chunk_message is None or chunk_message == "":
                continue
            self.staging.append(chunk_message)
            staged = ''.join(self.staging)
            # if staged contains any comma, period, exclaimation mark, question mark, or colon, it is a complete sentence
            # pop the last recognition from self.staging and append it to self.response
            if staged != "" and any([c in staged for c in sentence_endings]):
                self.staging = [""]
                if callback:
                    await callback(staged)

def test_openai_chat():
    openai = OpenAIChat()
    async def test_callback(staged):
        print(staged)
    import asyncio
    asyncio.run(openai.chat("Hello, how may I assist you?", callback=test_callback))