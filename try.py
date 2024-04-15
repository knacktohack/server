from core.integration.pinecone_integration import PineConeIntegration
from core.azure.message_queue import loopForChunkingQueue
from core.mongo.utils import MongoUtils
from core.azure.document_extractor import extractFullPageText

# print(MongoUtils.deleteCollectionData("users"))
loopForChunkingQueue(deleteMessage=True)
# data = extractFullPageText("https://knacktohackstorage.blob.core.windows.net/chunked/DATA_661d21dfb902850d25983697/InsiderTradingandIndianStockMarket.pdf")

# #write into a txt file
# with open("test.txt", "w") as f:
#     f.write(data)