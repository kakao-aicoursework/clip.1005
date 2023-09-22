import os
import glob
from langchain.memory import ConversationBufferMemory, FileChatMessageHistory

from helper.kakao_llm import KakaoLLM
from helper.kakao_history import KakaoHistory
from helper.kakao_util import KakaoUtil
from helper.kakao_chroma import KakaoChroma


KAKAO_SOCIAL_DOC = "./project_data_카카오소셜.txt"
KAKAO_SYNC_DOC = "./project_data_카카오싱크.txt"
KAKAO_CHANNEL_DOC = "./project_data_카카오톡채널.txt"

def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template

class KakaoChatbot:

    def __init__(self) -> None:
        self.llm = KakaoLLM()
        self.history = KakaoHistory.new_history()
        self.chroma = KakaoChroma()

    def answer(self, user_message):
        return self.strategy1(user_message)

    def strategy1(self, user_message):
        sink_template = read_prompt_template("./project_data_카카오싱크.txt")

        chain = self.llm.build_chain(
            system_message=f'''너는 카카오싱크 API에 대해 설명해주는 챗봇이다.
                            다음의 카카오싱크 설명서를 이해하여 assistant는 user의 카카오싱크에 대한 질문에 대해 자세히 잘 답변해야 한다.
                            {sink_template}
                            ''', 
            human_template="{qna}"
        )

        full_content_truncated = KakaoUtil.truncate_text(user_message, max_tokens=3500)

        ans = chain.run(qna=full_content_truncated)
        print("ans:", ans)
        return ans

            
    

