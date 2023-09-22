import os
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.schema import SystemMessage
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from helper.kakao_util import KakaoUtil

class KakaoLLM:
    def __init__(self, temperature=0.8, max_tokens=8000, model="gpt-3.5-turbo-16k") -> None:
        os.environ["OPENAI_API_KEY"] = KakaoUtil.load_api_key('api_key.key')
        self.llm = ChatOpenAI(temperature=temperature, max_tokens=max_tokens, model=model)

    def create_chain(self, template_path, output_key):
        return LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(
                template=KakaoUtil.read_file(template_path)
            ),
            output_key=output_key,
            verbose=True,
        )
    
    def build_chain(self, system_message, human_template):
        system_message_prompt = SystemMessage(content=system_message)
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                        human_message_prompt])
        chain = LLMChain(llm=self.llm, prompt=chat_prompt, verbose=True)
        return chain
    
            
    

