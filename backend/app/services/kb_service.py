"""
知识库检索
"""
from chromadb.api.models import Collection
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings

from langchain_chroma import Chroma
from app.core.config import settings
from langchain_openai import OpenAIEmbeddings

KB_DIR = settings.BASE_DIR / "data" / "kb"
CHROMA_DIR = settings.BASE_DIR / "data" / "chroma"

_collection = None

def get_collection() -> Collection:
    global _collection
    if _collection is not None:
        return _collection
    KB_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    emb = DashScopeEmbeddings(model="text-embedding-v4")

    vector_store = Chroma(
        collection_name="lab_kb",
        embedding_function=emb,
        persist_directory=str(CHROMA_DIR)
    )

    if vector_store._collection.count() == 0:
        loader = DirectoryLoader(KB_DIR, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        row_docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        split_docs = splitter.split_documents(row_docs)

        # 入库
        vector_store.add_documents(split_docs)
    _collection = vector_store
    return vector_store

def query_kb(question: str, top_n: int = 2):
    collection = get_collection()
    result = collection.similarity_search(question, k=2)
    return result

if __name__ == "__main__":
    collection = get_collection()
    def query_kb(question: str, top_n: int = 2):
        result = collection.similarity_search(question, k=2)
        return result


    res = query_kb("预约规则")
    # 打印检索到的文档内容和来源
    for r in res:
        print(r.page_content)