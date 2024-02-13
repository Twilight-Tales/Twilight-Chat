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

from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
load_dotenv()


# class BookMemory(BaseMemory, BaseModel):
#     """Memory class for book chapter content."""
#
#     # Define dictionary to store information about entities.
#     entities: dict = {}  # we are not using this
#
#     # Define key to pass information about entities into prompt.
#     memory_key: str = "chapter_context"
#
#     def clear(self):
#         self.entities = {}  # we are not using this, just a placeholder because it is required by the BaseMemory
#
#     @property
#     def memory_variables(self) -> List[str]:
#         """Define the variables we are providing to the prompt."""
#         return [self.memory_key]
#
#     def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
#         """Load the memory variables, in this case the entity key."""
#         with open("books.txt", "r") as fp:
#             book = fp.read()
#         # Return combined information about entities to put into context.
#         return {self.memory_key: book}
#
#     def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
#         """Save context from this conversation to buffer."""
#         # We are using static knowledge, so we don't need to save anything.
#         pass

@cl.on_chat_start
async def on_chat_start():
    llm = ChatOpenAI(streaming=True, temperature=0, model_name="gpt-4-1106-preview")
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
