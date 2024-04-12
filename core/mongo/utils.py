from dotenv import load_dotenv
import os
from datetime import datetime
from datetime import date

load_dotenv()
from pymongo import MongoClient

mongoUrl = os.getenv("MONGO_URL")
dbName = os.getenv("MONGO_DB")
questionCollection = os.getenv("QUESTION_COLLECTION")
chatCollection = os.getenv("CHAT_COLLECTION")
violationCollection = os.getenv("VIOLATION_COLLECTION")

"""
question is a dictionary with the following keys
{
    "question": "What is the capital of Nigeria?",
    "priority": 0.5,
    "organization_id": "12345"
}

chats is a dictionary with the following keys

{
    "user_id": "12345",
    "conversation_id": "12345",
    "organization_id": "12345",
    "messages": [
        {
            "type": "human",
            "content": "Hello"
        },
        {
            "type": "ai",
            "content": "Hi"
        }
    ]
}

violation is a dictionary with the following keys

{
    "user_id": "12345",
    "organization_id": "12345",
    "conversation_id": "12345",
    "violation_question": "What is the capital of Nigeria?",
    "violation_priority": 5,
    "date": "2021-09-01"
}

"""


class MongoUtils:
    client = MongoClient(mongoUrl)

    @staticmethod
    def insertDocument(collectionName, document):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        result = collection.insert_one(document)
        return result.inserted_id

    @staticmethod
    def queryDocuments(collectionName, query={}):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        documents = collection.find(query)
        return list(documents)

    @staticmethod
    def deleteDocuments(collectionName, query={}):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        result = collection.delete_many(query)
        return result.deleted_count

    @staticmethod
    def queryAll(collectionName):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        documents = collection.find()
        return list(documents)

    @staticmethod
    def queryOne(collectionName, query={}):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        document = collection.find_one(query)
        return document

    @staticmethod
    def updateDocument(collectionName, query, update):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        result = collection.update_one(query, update)
        return result.modified_count

    @staticmethod
    def insertQuestion(question):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.insert_one(question)
        return result.inserted_id

    @staticmethod
    def queryByQuestion(question):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        document = collection.find_one(
            {"question": {"$regex": question, "$options": "i"}}
        )
        return list(document)

    @staticmethod
    def queryByPriorityGreaterThan(priority):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        documents = collection.find({"priority": {"$gt": priority}})
        return list(documents)

    @staticmethod
    def deleteAll(collectionName):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        result = collection.delete_many({})
        return result.deleted_count

    @staticmethod
    def queryByPriorityLessThan(priority):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        documents = collection.find({"priority": {"$lt": priority}})
        return list(documents)

    @staticmethod
    def insertChat(chat):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        result = collection.insert_one(chat)
        return result.inserted_id

    @staticmethod
    def queryChatByUserId(userId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        documents = collection.find({"user_id": userId})
        return list(documents)

    @staticmethod
    def queryChatByConversationId(conversationId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        documents = collection.find({"conversation_id": conversationId})
        return list(documents)

    @staticmethod
    def queryQuestionByOrganizationId(organizationId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        documents = collection.find({"organization_id": organizationId})
        return list(documents)

    @staticmethod
    def queryChatByUserIdAndConversationId(userId, conversationId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        documents = collection.find(
            {"user_id": userId, "conversation_id": conversationId}
        )
        return list(documents)

    @staticmethod
    def queryChatByOrganizationId(organizationId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        documents = collection.find({"organization_id": organizationId})
        return list(documents)

    @staticmethod
    def insertViolation(violation):
        client = MongoUtils.client

        # set current date for violation
        violation["date"] = datetime.now().strftime("%Y-%m-%d")
        db = client[dbName]
        collection = db[violationCollection]
        result = collection.insert_one(violation)
        return result.inserted_id

    @staticmethod
    def queryViolationByUserId(userId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find({"user_id": userId})
        return list(documents)

    @staticmethod
    def queryViolationByOrganizationId(organizationId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find({"organization_id": organizationId})
        return list(documents)

    @staticmethod
    def queryViolationByOrganizationIdAndUserId(organizationId, userId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find(
            {"organization_id": organizationId, "user_id": userId}
        )
        return list(documents)

    @staticmethod
    def queryViolationByDateInRangeAndUserId(
        startDate, endDate, userId, organizationId
    ):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find(
            {
                "date": {"$gte": startDate, "$lte": endDate},
                "user_id": userId,
                "organization_id": organizationId,
            }
        )
        return list(documents)

    @staticmethod
    def queryViolationByDateInRangeAndOrganizationId(
        startDate, endDate, organizationId
    ):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find(
            {
                "date": {"$gte": startDate, "$lte": endDate},
                "organization_id": organizationId,
            }
        )
        return list(documents)
