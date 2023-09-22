from datetime import datetime
from pynecone.base import Base
import pynecone as pc

from helper.kakao_chatbot import KakaoChatbot

kakao_chatbot = KakaoChatbot()

###########################################################
# Web

class Message(Base):
    original_text: str
    text: str
    created_at: str

class State(pc.State):
    """The app state."""

    text: str = ""
    screen = []
    messages: list[Message] = []

    def output(self) -> str:
        print("output in ", self.text)
        if not self.text.strip():
            return "Answer will appear here."
        ans = kakao_chatbot.answer(self.text)
        return ans

    def post(self):
        print(self.text)
        self.messages += [
            Message(
                original_text=self.text,
                text=self.output(),
                created_at=datetime.now().strftime("%B %d, %Y %I:%M %p")
            )
        ]

###########################################################
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
            text_box(message.text),
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
            text_box("안녕하세요. 카카오 챗봇 서비스를 시작합니다. 궁금하신 내용을 물어보세요!"),
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
