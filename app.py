import os

from langchain_community.chat_models import ChatOpenAI

import chainlit as cl

from typing import Any, Dict, List, Optional
from langchain.schema import BaseMemory
from pydantic import BaseModel

from langchain.chains import ConversationChain
from langchain.memory import (
    CombinedMemory,
    ConversationBufferMemory,
)

import bookclub_backend as db
DB = db.DatabaseDriver()

from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()

@cl.on_chat_start
async def on_chat_start():
    llm = ChatOpenAI(streaming=True, temperature=0, model_name="gpt-4-1106-preview")
    template = """
Objective: You are the host of a bookclub that helps elderly people with dementia. 
You have to prompt them and see whether or not they fully understand the content of the book. 
Context will be provided and generate prompts based on that. 
Ask open-ended questions but make sure that a 5th grader could answer them. 
After a conversation has concluded, ask a question relating to the book again and then move on to the next chapter. 
Make sure that it prompts the user to want to read the next chapter. 
Tailor it to elderly people. 
Only ask one question per time and keep them less than or equal to 2 sentences. 
Pause and wait for the user to give a response to the question, then analyze the response given by the elderly person and provide feedback as well as the next question.

Book chapter:
{chapter_context}

Current conversation:
{chat_history}
Elderly: {input}
host:"""
    prompt = PromptTemplate(
        input_variables=["chat_history", "input", "chapter_context"], template=template
    )

    with open("books.txt", "r", encoding='utf-8') as fp:
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
# async def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
#     # Fetch the user matching username from your database
#     # and compare the hashed password with the value stored in the database
#     success, user = db.login_user(username, password)
#     if success:
#         return user.serialize()
#     else:
#         return None
    """
    if (username, password) == (os.environ.get('USERNAME'), os.environ.get('PASSWORD')):
        return cl.AppUser(username="patient", role="ADMIN", provider="credentials")
    else:
        return None
    """
    
