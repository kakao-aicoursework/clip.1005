import os
import glob
from langchain.memory import ConversationBufferMemory, FileChatMessageHistory

HISTORY_DIR = os.path.join("./", "chat_histories")

class KakaoHistory:

    def load_conversation_history(conversation_id: str):
        file_path = os.path.join(HISTORY_DIR, f"{conversation_id}.json")
        return FileChatMessageHistory(file_path)

    histories = {}
    for json_file in glob.glob(os.path.join(HISTORY_DIR, "*.json")):
        conversation_id = os.path.basename(json_file).split(".")[0]
        n = int(conversation_id)
        histories[n] = load_conversation_history(conversation_id)

    @staticmethod
    def new_history():
        new_id = max(KakaoHistory.histories.keys(), default=0) + 1
        history = KakaoHistory.load_conversation_history(new_id)
        KakaoHistory.histories[new_id] = history
        return KakaoHistory(new_id)

    def __init__(self, conversation_id) -> None:
        self.conversation_id = conversation_id
        self.history: FileChatMessageHistory = None
        if conversation_id in KakaoHistory.histories:
            self.history = KakaoHistory.histories[conversation_id]
        else:
            raise ValueError(f"Conversation ID {conversation_id} not found")

    def log_user_message(self, user_message: str):
        self.history.add_user_message(user_message)


    def log_bot_message(self, bot_message: str):
        self.history.add_ai_message(bot_message)


    def get_chat_history(self):
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="user_message",
            chat_memory=self.history,
        )

        return memory.buffer
    
            
    

