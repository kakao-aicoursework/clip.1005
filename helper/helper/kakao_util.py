import os
from langchain.utilities import DuckDuckGoSearchAPIWrapper
import tiktoken


class KakaoUtil:

    search = DuckDuckGoSearchAPIWrapper()
    search.region = 'kr-kr'

    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

    @staticmethod
    def truncate_text(text, max_tokens=3000):
        enc = KakaoUtil.enc
        tokens = enc.encode(text)
        if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
            return text
        return enc.decode(tokens[:max_tokens])
    
            
    

