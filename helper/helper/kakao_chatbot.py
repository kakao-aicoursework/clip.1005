import os
import glob
from langchain.memory import ConversationBufferMemory, FileChatMessageHistory

from helper.kakao_llm import KakaoLLM
from helper.kakao_history import KakaoHistory
from helper.kakao_util import KakaoUtil
from helper.kakao_chroma import KakaoChroma

# 제목 번호 리스트 표 - 설명 url
KAKAO_SOCIAL_DOC = "./project_data_카카오소셜.txt"
KAKAO_SYNC_DOC = "./project_data_카카오싱크.txt"
KAKAO_CHANNEL_DOC = "./project_data_카카오톡채널.txt"

# 프롬프트 템플릿
CUR_DIR = "./"
TUTORIAL_STEP1_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/tutorials_analyze.txt")
TUTORIAL_STEP2_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/tutorials_guide.txt")
USAGE_STEP1_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/usage_analyze.txt")
USAGE_STEP2_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/usage_guide.txt")
DEFAULT_RESPONSE_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/default_response.txt")
INTENT_LIST_TXT = os.path.join(CUR_DIR, "prompt/intent_list.txt")
INTENT_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/parse_intent.txt")
SUMMARIZE_TRANSLATE_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/summarize_translate.txt")
SEARCH_VALUE_CHECK_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/search_value_check.txt")
SEARCH_COMPRESSION_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt/search_compress.txt")


class KakaoChatbot:

    def __init__(self) -> None:
        self.llm: KakaoLLM = KakaoLLM()
        self.history: KakaoHistory = KakaoHistory.new_history()
        self.chroma: KakaoChroma = KakaoChroma()
        self.updateDocsInChroma()

    def answer(self, user_message):
        return self.strategy2(user_message)
    
    def updateDocsInChroma(self):
        for template_path in [KAKAO_SOCIAL_DOC, KAKAO_SYNC_DOC, KAKAO_CHANNEL_DOC]:
            self.chroma.upload_embedding_from_file(template_path)

    def strategy1(self, user_message):
        sink_template = KakaoUtil.read_file(KAKAO_SYNC_DOC)

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

    def strategy2(self, user_message):

        cc = self.llm.create_chain
        usage_step1_chain = cc(
            template_path=USAGE_STEP1_PROMPT_TEMPLATE,
            output_key="usage_analysis",
        )
        usage_step2_chain = cc(
            template_path=USAGE_STEP2_PROMPT_TEMPLATE,
            output_key="output",
        )
        tutorial_step1_chain = cc(
            template_path=TUTORIAL_STEP1_PROMPT_TEMPLATE,
            output_key="tutorial_analysis",
        )
        tutorial_step2_chain = cc(
            template_path=TUTORIAL_STEP2_PROMPT_TEMPLATE,
            output_key="output",
        )
        parse_intent_chain = cc(
            template_path=INTENT_PROMPT_TEMPLATE,
            output_key="intent",
        )
        default_chain = cc(
            template_path=DEFAULT_RESPONSE_PROMPT_TEMPLATE,
            output_key="output"
        )
        summarize_translate_chain = cc(
            template_path=SUMMARIZE_TRANSLATE_PROMPT_TEMPLATE,
            output_key="output",
        )

        search_value_check_chain = cc(
            template_path=SEARCH_VALUE_CHECK_PROMPT_TEMPLATE,
            output_key="output",
        )
        search_compression_chain = cc(
            template_path=SEARCH_COMPRESSION_PROMPT_TEMPLATE,
            output_key="output",
        )


        context = dict(user_message=user_message)
        context["input"] = context["user_message"]
        context["intent_list"] = KakaoUtil.read_file(INTENT_LIST_TXT)
        context["chat_history"] = self.history.get_chat_history()

        intent = parse_intent_chain.run(context)
        # Usage (How-to)
        # Authentication (Login)
        # Endpoint (Functions)
        # Format (Structure)
        # Retrieval (Data)
        # Tutorials (Examples)
        # Security (Protection)

        if intent == "Usage":
            context["related_documents"] = self.chroma.query_db(context["user_message"])

            for step in [usage_step1_chain, usage_step2_chain]:
                context = step(context)
            answer = context[step.output_key]

        elif intent == "Tutorials":
            context["related_documents"] = self.chroma.query_db(context["user_message"])

            for step in [tutorial_step1_chain, tutorial_step2_chain]:
                context = step(context)
            answer = context[step.output_key]
            
        else:
            context["related_documents"] = self.chroma.query_db(context["user_message"])

            context["related_web_search_results"] = KakaoUtil.query_web_search(context["user_message"])

            has_value = search_value_check_chain.run(context)
            print(has_value)
            context["compressed_web_search_results"] = ""
            if has_value == "Y":
                context["compressed_web_search_results"] = search_compression_chain.run(context)

            answer = default_chain.run(context)

        context["answer"] = answer
        answer = summarize_translate_chain.run(context)

        self.history.log_user_message(user_message)
        self.history.log_bot_message(answer)

        return answer
    

