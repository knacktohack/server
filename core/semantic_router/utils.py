from .create_index import createIndex,returnIndex
from semantic_router.encoders import OpenAIEncoder
import os


indexName = "knacktohack"

encoder = OpenAIEncoder(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def insertRoute(routeName,utterances):
    index = returnIndex(indexName)
    lenUtterances = len(utterances)
    
    routes = []
    vectors = encoder(utterances)
    
    for i in range(lenUtterances):
        routes.append(routeName)
        
    return index.add(embeddings=vectors,routes = routes, utterances=utterances)


def deleteAll():
    index = returnIndex(indexName)
    return index.delete_all()