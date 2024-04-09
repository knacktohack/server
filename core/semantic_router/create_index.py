import os
from getpass import getpass
from semantic_router.index import PineconeIndex
from dotenv import load_dotenv

load_dotenv()

def createIndex(name):
    index = PineconeIndex(index_name=name, api_key=os.getenv("PINECONE_API_KEY"),dimensions=1536)
    return index


def returnIndex(name):
    index = PineconeIndex(index_name=name, api_key=os.getenv("PINECONE_API_KEY"),dimensions=1536)
    return index