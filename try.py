from core.integration.pinecone_integration import PineConeIntegration
from core.azure.message_queue import loopForChunkingQueue
from core.mongo.utils import MongoUtils

# print(MongoUtils.deleteCollectionData("users"))
# loopForChunkingQueue(deleteMessage=True)