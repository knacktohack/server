import os
from getpass import getpass
from semantic_router.index import PineconeIndex
from dotenv import load_dotenv

load_dotenv()

defaultName = os.getenv("SEMANTIC_INDEX_NAME")

def createIndex(name= defaultName):
    index = PineconeIndex(index_name=name, api_key=os.getenv("PINECONE_API_KEY"),dimensions=1536)
    return index


def returnIndex(name= defaultName):
    index = PineconeIndex(index_name=name, api_key=os.getenv("PINECONE_API_KEY"),dimensions=1536)
    index.index = index._init_index()
    return index