import chainlit as cl
from chainlit.types import ThreadDict

from chatbot import setup_openai, setup_mistral, setup_llama, remove_matching_suffix, stop_tokens

from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable.config import RunnableConfig

from dotenv import load_dotenv

load_dotenv()

str_gpt4 = "GPT-4"
str_mistral = "Mistral"
str_llama = "Llama"

llm_dict = {
    str_gpt4: setup_openai,
    str_mistral: setup_mistral,
    str_llama: setup_llama
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
    if llm_choice == str_gpt4:
        memory = ConversationBufferMemory(memory_key="history", input_key="input",
                                          return_messages=True)
    else:
        memory = ConversationBufferMemory(memory_key="history", input_key="input",
                                          human_prefix="Elderly", ai_prefix="Host",
                                          return_messages=False)
    cl.user_session.set("memory", memory)
    llm_dict[llm_choice]()


@cl.on_message
async def on_message(message: cl.Message):
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory

    runnable = cl.user_session.get("runnable")  # type: Runnable

    res = cl.Message(content="")

    async for chunk in runnable.astream(
        {"input": message.content.strip()},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await res.stream_token(chunk)

    await res.send()

    memory.chat_memory.add_user_message(message.content.strip())
    memory.chat_memory.add_ai_message(remove_matching_suffix(res.content.strip(), stop_tokens))

# @cl.password_auth_callback
# def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
#     # Fetch the user matching username from your database
#     # and compare the hashed password with the value stored in the database
#     if (username, password) == (os.environ.get('USERNAME'), os.environ.get('PASSWORD')):
#         return cl.AppUser(username="patient", role="ADMIN", provider="credentials")
#     else:
#         return None
