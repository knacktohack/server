from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from dotenv import load_dotenv
from core.chunker import getChunksFromFiles
import os
load_dotenv()

embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

class RagIntegration:
    vectorStore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=embeddings
    )
    
    @staticmethod
    def addText(text: str):
        return RagIntegration.vectorStore.add_texts([text])
    
    @staticmethod
    def getRetriever():
        return RagIntegration.vectorStore.as_retriever()
    
    @staticmethod
    def addDocumentWithUrl(pdfUrl: str):
        chunks = getChunksFromFiles(pdfUrl,chunk_size=2000)
        return RagIntegration.vectorStore.add_texts(chunks['chunks'])