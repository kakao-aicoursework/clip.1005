import os
from langchain.document_loaders import (
    NotebookLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import SystemMessage
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma


CHROMA_PERSIST_DIR = os.path.join("./", "chroma_persist")
CHROMA_COLLECTION_NAME = "kakao-api-chatbot"

LOADER_DICT = {
    "py": TextLoader,
    "md": UnstructuredMarkdownLoader,
    "ipynb": NotebookLoader,
}

class KakaoChroma:
    def __init__(self) -> None:
        self._db = Chroma(
                    persist_directory=CHROMA_PERSIST_DIR,
                    embedding_function=OpenAIEmbeddings(),
                    collection_name=CHROMA_COLLECTION_NAME,
                )
        self._retriever = self._db.as_retriever()

    def query_db(self, query: str, use_retriever: bool = False) -> list[str]:
        if use_retriever:
            docs = self._retriever.get_relevant_documents(query)
        else:
            docs = self._db.similarity_search(query)

        str_docs = [doc.page_content for doc in docs]
        return str_docs

    def upload_embedding_from_file(self, file_path):
        loader = LOADER_DICT.get(file_path.split(".")[-1])
        if loader is None:
            raise ValueError("Not supported file type")
        documents = loader(file_path).load()

        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)
        print(docs, end='\n\n\n')

        Chroma.from_documents(
            docs,
            OpenAIEmbeddings(),
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR,
        )
        print('db success')

    def upload_embeddings_from_dir(dir_path):
        failed_upload_files = []

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".py") or file.endswith(".md") or file.endswith(".ipynb"):
                    file_path = os.path.join(root, file)

                    try:
                        self.upload_embedding_from_file(file_path)
                        print("SUCCESS: ", file_path)
                    except Exception as e:
                        print("FAILED: ", file_path + f"by({e})")
                        failed_upload_files.append(file_path)
