"""Welcome to Pynecone! This file outlines the steps to create a basic app."""

# Import pynecone.
import openai
import os
from datetime import datetime
from pynecone.base import Base

from typing import List
import asyncio
from concurrent.futures import ProcessPoolExecutor
import pynecone as pc
import requests
from bs4 import BeautifulSoup
import pandas as pd
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import SystemMessage

from langchain.utilities import DuckDuckGoSearchAPIWrapper
import tiktoken

def load_api_key(filename='api_key.txt'):
    try:
        with open(filename, 'r') as file:
            api_key = file.read()
            return api_key.strip()
    except Exception as e:
        print(f"API 키 읽기 중 오류 발생: {str(e)}")
        return None

import os
os.environ["OPENAI_API_KEY"] = load_api_key()


###########################################################
# Helpers

def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template

def build_chain(llm):
    sink_template = read_prompt_template("./project_data_카카오싱크.txt")
    
    system_message = f'''너는 카카오싱크 API에 대해 설명해주는 챗봇이다.
    다음의 카카오싱크 설명서를 이해하여 assistant는 user의 카카오싱크에 대한 질문에 대해 자세히 잘 답변해야 한다.
    {sink_template}
    '''
    system_message_prompt = SystemMessage(content=system_message)

    human_template = "{qna}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                    human_message_prompt])

    chain = LLMChain(llm=llm, prompt=chat_prompt, verbose=True)
    return chain



def truncate_text(text, max_tokens=3000):
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
        return text
    return enc.decode(tokens[:max_tokens])


def task(qna):
    full_content_truncated = truncate_text(qna, max_tokens=3500)

    ans = chain.run(qna=full_content_truncated)
    print("ans:", ans)

    return ans

###########################################################
# Instances
llm = ChatOpenAI(temperature=0.8)

search = DuckDuckGoSearchAPIWrapper()
search.region = 'kr-kr'

enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

chain = build_chain(llm)


###########################################################



def dev_chat_bot_using_chatgpt(text) -> str:
    return task(text)

###########################################################
# Web


class Message(Base):
    original_text: str
    text: str
    created_at: str
    to_lang: str


class State(pc.State):
    """The app state."""

    text: str = ""
    screen = []
    messages: list[Message] = []
    src_lang: str = "한국어"
    trg_lang: str = "영어"

    def output(self) -> str:
        print("output in ", self.text)
        if not self.text.strip():
            return "Translations will appear here."
        ans = dev_chat_bot_using_chatgpt(self.text)
        return ans

    def post(self):
        print(self.text)
        # return
        self.messages += [
            Message(
                original_text=self.text,
                text=self.output(),
                created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
                to_lang=self.trg_lang,
            )
        ]


# Define views.


def header():
    """Basic instructions to get started."""
    return pc.box(
        pc.text("Translator 🗺", font_size="2rem"),
        pc.text(
            "Translate things and post them as messages!",
            margin_top="0.5rem",
            color="#666",
        ),
    )


def down_arrow():
    return pc.vstack(
        pc.icon(
            tag="arrow_down",
            color="#666",
        )
    )


def text_box(text):
    return pc.text(
        text,
        background_color="#fff",
        padding="1rem",
        border_radius="8px",
    )


def message(message):
    return pc.box(
        pc.vstack(
            text_box(message.original_text),
            # down_arrow(),
            text_box(message.text),
            # pc.box(
            #     pc.text(message.to_lang),
            #     pc.text(" · ", margin_x="0.3rem"),
            #     pc.text(message.created_at),
            #     display="flex",
            #     font_size="0.8rem",
            #     color="#666",
            # ),
            spacing="0.3rem",
            align_items="left",
        ),
        background_color="#f5f5f5",
        padding="1rem",
        border_radius="8px",
    )



def index():
    """The main view."""
    return pc.container(

        pc.box(
            text_box("안녕하세요. 카카오싱크 챗봇 서비스를 시작합니다. 궁금하신 내용을 물어보세요!"),
            background_color="#f5f5f5",
            padding="1rem",
            border_radius="8px",
        ),

        pc.vstack(
            pc.foreach(State.messages, message),
            margin_top="2rem",
            spacing="1rem",
            align_items="left"
        ),


        pc.input(
            placeholder="Text to question",
            on_blur=State.set_text,
            margin_top="1rem",
            border_color="#eaeaef"
        ),
        pc.button("Submit", on_click=State.post, margin_top="1rem"),
        
        padding="2rem",
        max_width="600px"
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Kakaosink Chatbot")
app.compile()
