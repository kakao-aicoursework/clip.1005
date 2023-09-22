import os
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.schema import SystemMessage
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)

def load_api_key(filename='api_key.key'):
    try:
        with open(filename, 'r') as file:
            api_key = file.read()
            return api_key.strip()
    except Exception as e:
        print(f"API 키 읽기 중 오류 발생: {str(e)}")
        return None

class KakaoLLM:
    def __init__(self, temperature=0.8, max_tokens=8000, model="gpt-3.5-turbo-16k") -> None:
        os.environ["OPENAI_API_KEY"] = load_api_key()
        self.llm = ChatOpenAI(temperature=temperature, max_tokens=max_tokens, model=model)

    def create_chain(self, template, output_key):
        return LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(
                template=template
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
    
            
    

