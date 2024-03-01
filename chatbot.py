from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import VLLMOpenAI

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.memory import ConversationBufferMemory

from chainlit.playground.config import add_llm_provider
from chainlit.playground.providers.langchain import LangchainGenericProvider

import chainlit as cl
from operator import itemgetter
from dotenv import load_dotenv
import os

load_dotenv()


system_instruction = """
Your are a bookclub host of an one-on-one session for elderly individuals,
your job is to nurture a love for reading and encourage ongoing engagement with books. 
Ask a few simple and open ended easy questions about the book chapter that the elderly just finished reading.
Then end the conversation by giving hints of what happens next in the book, making them look forward to the next 
session. 
Keep your question short and sweet, no more than two sentences, and ensure it’s crafted in a way that feels more like a casual chat than a quiz.

Book chapter for discussion today:
------
{chapter_context}
------

Use the chat history below for context to make a meaningful conversation. 
End the conversation when you detect the elderly feels tired.
"""

with open("books.txt", "r") as fp:
    book = fp.read()


def setup_openai():
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    model = ChatOpenAI(streaming=True,
                       temperature=0.1,
                       model_name="gpt-4-1106-preview")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    runnable = (
        {"chapter_context": RunnableLambda(lambda x: book), "input": itemgetter("input")}
        | RunnablePassthrough.assign(history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
        | prompt
        | model
        | StrOutputParser()
    )
    cl.user_session.set("runnable", runnable)


def setup_mistral():
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    model = VLLMOpenAI(
        openai_api_key="EMPTY",
        # openai_api_base="http://host.docker.internal:8000/v1",
        openai_api_base=os.environ.get('VLLM_URL'),
        model_name=os.environ.get('MISTRAL_ID'),
        max_tokens=60,
        temperature=0.7,
        # frequency_penalty=0.2,
        model_kwargs={"stop": ['\nHuman:', 'Elderly', 'Host:',
                               '\nElderly:',
                               '\n```\n',
                               '<<END>>',
                               '\n\n']},
    )

    prompt = PromptTemplate(
        input_variables=["history", "input", "chapter_context"],
        template=system_instruction + "\n\nChat History:\n{history}\n\nElderly: {input}\n\nHost:"
    )

    runnable = (
        {"chapter_context": RunnableLambda(lambda x: book[:200]), "input": itemgetter("input")}
        | RunnablePassthrough.assign(history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
        | prompt
        | model
        | StrOutputParser()
    )
    cl.user_session.set("runnable", runnable)

    # Add the LLM provider
    add_llm_provider(
        LangchainGenericProvider(
            # It is important that the id of the provider matches the _llm_type
            id=model._llm_type,
            # The name is not important. It will be displayed in the UI.
            name=os.environ.get('MISTRAL_ID'),
            # This should always be a Langchain llm instance (correctly configured)
            llm=model,
            # If the LLM works with messages, set this to True
            is_chat=False
        )
    )


def setup_llama():
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    model = VLLMOpenAI(
        openai_api_key="EMPTY",
        # openai_api_base="http://host.docker.internal:8000/v1",
        openai_api_base=os.environ.get('VLLM_URL'),
        model_name=os.environ.get('LLAMA_ID'),
        max_tokens=60,
        temperature=0.1,
        model_kwargs={"stop": ['\nHuman:', 'Elderly:',
                               '\nElderly:'
                               '\n```\n',
                               '<<END>>',
                               '</s>',
                               '\n\n']},
    )

    prompt = PromptTemplate(
        input_variables=["history", "input", "chapter_context"],
        template=system_instruction + "\n\nChat History:\n{history}\n\nElderly: {input}\n\nHost:"
    )

    runnable = (
            {"chapter_context": RunnableLambda(lambda x: book), "input": itemgetter("input")}
            | RunnablePassthrough.assign(history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
            | prompt
            | model
            | StrOutputParser()
    )
    cl.user_session.set("runnable", runnable)

    # Add the LLM provider
    add_llm_provider(
        LangchainGenericProvider(
            # It is important that the id of the provider matches the _llm_type
            id=model._llm_type,
            # The name is not important. It will be displayed in the UI.
            name=os.environ.get('LLAMA_ID'),
            # This should always be a Langchain llm instance (correctly configured)
            llm=model,
            # If the LLM works with messages, set this to True
            is_chat=False
        )
    )
