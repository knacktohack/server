# # from PyPDF2 import PdfReader

# # reader = PdfReader("out/demo.pdf")

# # text = ""
# # for page in reader.pages:
# #   text += page.extract_text() + "\n"

# # print(text)

# # from pinecone import Pinecone

# # pc = Pinecone(api_key="")
# # index = pc.Index("test")

# # from core.semantic_router.create_index import createIndex
# # from core.semantic_router.utils import insertRoute,deleteAll
# # from core.question_generation.question_generator import QuestionGenerator
from core.integration.pinecone_integration import PineConeIntegration
# # # from core.chunker import getChunksFromFiles
# # from core.kors.question_extractor import QuestionExtractor
# # from core.rag.utils import RagIntegration
# from core.azure.blob_storage import uploadToBlobStorage,getAllFiles
from core.azure.message_queue import publishToChunkingQueue,loopForChunkingQueue
from core.mongo.utils import MongoUtils
from pymongo import MongoClient
from core.pinecone.question_utils import PineconeClient
# # print(pc.describe_index("test"))

# # res = index.upsert(vectors=[
# #   {
# #     "id": "1",
# #     "values": [0.1, 0.2, 0.3, 0.1],
# #     "metadata": {
# #       "text": "interesting text",
# #       "doc_id": 2
# #     }
# #   }, 
# #   {
# #     "id": "2",
# #     "values": [0.1, 0.1, 0.1, 0.2],
# #     "metadata": {
# #       "text": "random text",
# #       "doc_id": 1
# #     }
# #   }, 
# #   {
# #     "id": "3",
# #     "values": [0.6, 0.2, 0.3, 0.6],
# #     "metadata": {
# #       "text": "some text",
# #       "doc_id": 1
# #     }
# #   }, 
# #   ])

# # print(res)

# # res = index.query(
# #     vector=[0.1, 0.1, 0.1, 0.1],
# #     top_k=4,
# #     include_values=True,
# #     include_metadata=True,
# #     filter={"doc_id": {"$eq": 1}}
# # )

# # print(res)
# # print([v["metadata"]["text"] for v in res["matches"]])

if __name__ == "__main__":
#     # take input considering newlines
#     # input = input("Enter the text: ")
#     # print(QuestionExtractor.extractQuestions(input))
#     # # #extract questions
#     # # output = QuestionGenerator.generateQuestions(input)
#     # # print(output)
#     # processChunk(input)
#     # deleteAll()
#     # PineConeIntegration.deleteAll()
#     # PineConeIntegration.processChunk(getChunksFromFiles("https://knacktohackstorage.blob.core.windows.net/chunked/sample.pdf")['chunks'][1])
    
#     # for question in questions['question_parser']['question']:
#     #     generatedQuestions = QuestionGenerator.generateQuestions(question)
#     #     print(question)
#     #     print(generatedQuestions)
#     # insertRoute("test", ["hello", "world"])
#     text = input("Enter the text: ")
#     # # RagIntegration.addText(text)
#     # print(QuestionExtractor.extractQuestions(text))    
#     # print(RagIntegration.addDocumentWithUrl(text))
#     # uploadToBlobStorage("/Users/adityaganguly/college/MG/sample1.pdf","sample1.pdf")
#     # loopForChunkingQueue(deleteMessage=False)
#     # publishToChunkingQueue({"url":"https://knacktohackstorage.blob.core.windows.net/chunked/sample.pdf"})
#     print(getAllFiles())
#     PineConeIntegration.processChunk(text)
    #MongoUtils.insertQuestion({"question": "What is the capital of India?", "organization_id": "1", "priority": 5})
    # MongoUtils.deleteAll("questions")
    # print(MongoUtils.queryByPriorityGreaterThan(8))
    # print("Hello")
    # loopForChunkingQueue(deleteMessage=True)
    # while True:
    #     inp = input("Enter the text: ")
    #     print(PineConeIntegration.getRoute(inp))
    
    # text = input("Enter the text: ")
    # PineConeIntegration.processChunk(text)
    print(MongoUtils.queryAllQuestions())
    # PineconeClient.createIndex()


# client = MongoClient("mongodb+srv://amartya:6411@cluster0.kvdsk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# db = client.knacktohack

# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
#     chats = db.chats
#     chat = {
#         "user_id": "user",
#         "history": [{"type": "user", "content": "something"}, {"type": "ai", "content": "anything"}]
#     }
#     chats.insert_one(chat)
#     print(db, chats)
# except Exception as e:
#     print(e)

# questions = db.questions

# try:
#     question = {
#         "question": "some random question",
#         "organization_id": "1",
#         "priority": 5
#     } 
#     res = questions.insert_one(question)
#     print("added", res.inserted_id)
# except Exception as e:
#     print(e)

# updated_question = "new random"
# try:
#     res = questions.find_one_and_update({"question": "some random question", "organization_id": "1"}, {"$set": {"priority": 8, "question": updated_question}})
    
#     print("updated", res)
# except Exception as e:
#     print(e)


