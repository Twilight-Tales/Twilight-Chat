import os

from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import VLLMOpenAI

import chainlit as cl

from typing import Any, Dict, List, Optional
from langchain.schema import BaseMemory
from pydantic import BaseModel

from langchain.chains import ConversationChain
from langchain.memory import (
    CombinedMemory,
    ConversationBufferMemory,
)

from langchain.prompts import PromptTemplate

from dotenv import load_dotenv

load_dotenv()

str_gpt4 = "GPT-4"
str_mistral = "Mistral"
str_llama = "Llama"

llm_dict = {
    str_gpt4: ChatOpenAI(streaming=True,
                         temperature=0,
                         model_name="gpt-4-1106-preview"),
    str_mistral: VLLMOpenAI(
        openai_api_key="EMPTY",
        # openai_api_base="http://host.docker.internal:8000/v1",
        openai_api_base=os.environ.get('VLLM_URL'),
        model_name=os.environ.get('MISTRAL_ID'),
        model_kwargs={"stop": ['\nHuman:', 'Elderly:',
                               '\nElderly:'
                               '\n```\n',
                               '<<END>>',
                               '</s>',
                               '\n\n']},
    ),
    str_llama: VLLMOpenAI(
        openai_api_key="EMPTY",
        # openai_api_base="http://host.docker.internal:8000/v1",
        openai_api_base=os.environ.get('VLLM_URL'),
        model_name=os.environ.get('LLAMA_ID'),
        model_kwargs={"stop": ['\nHuman:', 'Elderly:',
                               '\nElderly:'
                               '\n```\n',
                               '<<END>>',
                               '</s>',
                               '\n\n']},
    )
}


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name=str_gpt4,
            markdown_description="The underlying LLM model is **GPT-4**.",
            icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name=str_mistral,
            markdown_description="The underlying LLM model is **Mistral-7B-Instruct-v0.1**.",
            icon="https://picsum.photos/150",
        ),
        cl.ChatProfile(
            name=str_llama,
            markdown_description="The underlying LLM model is **Llama-13B-chat**.",
            icon="https://picsum.photos/200",
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    llm_choice = cl.user_session.get("chat_profile")
    llm = llm_dict[llm_choice]
    template = """
Objective: You are a bookclub host that helps elderly people. Ask questions about the chapter they just read to 
keep them engaging in the reading activity. To help them stay mentally and cognitively healthy.

Book chapter:
{chapter_context}

Current conversation:
{chat_history}
Elderly: {input}
Host:"""
    prompt = PromptTemplate(
        input_variables=["chat_history", "input", "chapter_context"], template=template
    )

    with open("books.txt", "r") as fp:
        book = fp.read()

    partial_prompt = prompt.partial(chapter_context=book)

    memory = ConversationBufferMemory(llm=llm,
                                      memory_key="chat_history", input_key="input",
                                      human_prefix="Elderly", ai_prefix="Host")

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
