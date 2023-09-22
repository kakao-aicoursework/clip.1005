import os
import tiktoken
from langchain.tools import Tool
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain.utilities import GoogleSearchAPIWrapper

class KakaoUtil:

    @staticmethod
    def load_api_key(filename):
        try:
            with open(filename, 'r') as file:
                api_key = file.read()
                return api_key.strip()
        except Exception as e:
            print(f"API 키 읽기 중 오류 발생: {str(e)}")
            return None

    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, "r") as f:
            contents = f.read()

        return contents

    @staticmethod
    def truncate_text(text, max_tokens=3000):
        tokens = enc.encode(text)
        if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
            return text
        return enc.decode(tokens[:max_tokens])
    
    @staticmethod
    def web_search_tool() -> Tool:
        return Tool(
            name="Google Search",
            description="Search Google for recent results.",
            func=googleSearch.run,
        )
    
    @staticmethod
    def query_web_search(user_message: str) -> str:
        search_tool = KakaoUtil.web_search_tool()

        return search_tool.run(user_message)
    


duckSearch = DuckDuckGoSearchAPIWrapper()
duckSearch.region = 'kr-kr'

api_key,ces_id = KakaoUtil.load_api_key('google_key.key').split('\n')
googleSearch = GoogleSearchAPIWrapper(
    google_api_key=os.getenv("GOOGLE_API_KEY",api_key),
    google_cse_id=os.getenv("GOOGLE_CSE_ID",ces_id)
)

enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

