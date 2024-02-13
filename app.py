import os

from langchain_community.chat_models import ChatOpenAI

import chainlit as cl

from genai import Client, Credentials
from genai.extensions.langchain import LangChainChatInterface
from genai.schema import DecodingMethod, TextGenerationParameters

from langchain.chains import ConversationChain
from langchain.memory import (
    CombinedMemory,
    ConversationBufferMemory,
)

from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()


@cl.on_chat_start
async def on_chat_start():
    # llm = ChatOpenAI(streaming=True, temperature=0, model_name="gpt-4-1106-preview")
    llm = LangChainChatInterface(
        model_id=os.environ.get('MODEL_ID'),
        client=Client(credentials=Credentials.from_env()),
        parameters=TextGenerationParameters(
            decoding_method=DecodingMethod.SAMPLE,
            max_new_tokens=300,
            min_new_tokens=10,
            temperature=0.5,
            top_k=50,
            top_p=1,
            stop_sequences=['\nElderly:',
                            '\n```\n',
                            '<<END>>',
                            '</s>',
                            '\n\n'],
            repetition_penalty=1,
        ),
    )
    template = """
Objective: You are a bookclub host that helps elderly people. Ask questions about the chapter they just read to 
keep them engaging in the reading activity. To help them stay mentally and cognitively healthy.

Book chapter:
{chapter_context}

Current conversation:
{chat_history}
Elderly: {input}
host:"""
    prompt = PromptTemplate(
        input_variables=["chat_history", "input", "chapter_context"], template=template
    )

    with open("books.txt", "r") as fp:
        book = fp.read()

    partial_prompt = prompt.partial(chapter_context=book)

    memory = ConversationBufferMemory(llm=llm,
                                                  memory_key="chat_history", input_key="input",
                                                  human_prefix="Patient", ai_prefix="Therapist")

    # book_memory = BookMemory(input_key="input")
    # # Combined: use multiple memories
    # # https://python.langchain.com/docs/modules/memory/multiple_memory
    # memory = CombinedMemory(memories=[conv_memory, book_memory])

    conversation = ConversationChain(llm=llm, verbose=True, memory=memory, prompt=partial_prompt)

    cl.user_session.set("chain", conversation)


@cl.on_message
async def on_message(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: ConversationChain
    res = await chain.arun(
        message.content, callbacks=[cl.AsyncLangchainCallbackHandler()]
    )
    await cl.Message(content=res).send()


# @cl.password_auth_callback
# def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
#     # Fetch the user matching username from your database
#     # and compare the hashed password with the value stored in the database
#     if (username, password) == (os.environ.get('USERNAME'), os.environ.get('PASSWORD')):
#         return cl.AppUser(username="patient", role="ADMIN", provider="credentials")
#     else:
#         return None
