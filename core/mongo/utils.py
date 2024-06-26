from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from datetime import date

load_dotenv()
from pymongo import MongoClient
from bson.objectid import ObjectId

mongoUrl = os.getenv("MONGO_URL")
dbName = os.getenv("MONGO_DB")
questionCollection = os.getenv("QUESTION_COLLECTION")
chatCollection = os.getenv("CHAT_COLLECTION")
violationCollection = os.getenv("VIOLATION_COLLECTION")
organizationCollection = os.getenv("ORGANIZATION_COLLECTION")
potentialViolationsCollection = os.getenv("POTENTIAL_VIOLATION_COLLECTION")
print(organizationCollection)
"""
question is a dictionary with the following keys
{
    "question": "What is the capital of Nigeria?",
    "priority": 0.5,
    "organization_id": "12345"
    "sample_questions: [
        
    ],
    "threshold":0.82
}

users

{
    user_name: "Aditya",
    user_id: "12345",
    organization_name: "12345",
    "user_email": "abc"
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
    "organization_name": "12345",
    "conversation_id": "12345",
    "violation_question": "What is the capital of Nigeria?",
    "violation_priority": 5,
    "score":0.8,
    "date": "2021-09-01"
}

organization is of the type

{
    "organization_name": "KnackToHack"
}

potentialViolations is of the type

{
    "question_name": "What is the capital of Nigeria?",,
    "prompt": "What is the capital of Nigeria?",
    "score": 0.8,
}

"""


def removeAndInsertId(documents):
    for document in documents:
        if "_id" in document:
            document["id"] = document["_id"].__str__()
            del document["_id"]
    return documents


class MongoUtils:
    client = MongoClient(mongoUrl)

    @staticmethod
    def updateUserDocument(collectionName, query, update):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        MongoUtils.insertUserIfNotExists(query["user_id"])
        result = collection.update_one(query, {"$set": update})
        return result.modified_count
    
    
    @staticmethod
    def queryAll(collectionName):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        documents = collection.find({})
        documents = [document for document in documents]
        documents = removeAndInsertId(documents)
        return list(documents)

    @staticmethod
    def queryUserIdAndSeverityScoreDescending():
        client = MongoUtils.client
        db = client[dbName]
        collection = db["users"]
        documents = collection.find().sort("severity_score", -1)

        documents = [document for document in documents]
        print(documents)
        if len(documents) == 0:
            return []
        documents = removeAndInsertId(documents)
        documents = [
            {
                "user_id": document["user_id"],
                "severity_score": (
                    document["severity_score"] if "severity_score" in document else 0
                ),
            }
            for document in documents
        ]
        return list(documents)

    @staticmethod
    def deleteCollectionData(collectionName):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        result = collection.delete_many({})
        return result.deleted_count
    
    
    @staticmethod
    def deleteFromCollectionById(collectionName, id):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        result = collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count

    @staticmethod
    def upsertDocument(collectionName, query, update):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[collectionName]
        result = collection.update_one(query, {"$set": update}, upsert=True)
        return result.modified_count

    @staticmethod
    def insertUserIfNotExists(userId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db["users"]
        document = collection.find_one({"user_id": userId})
        if document is None:
            collection.insert_one({"user_id": userId})
        return document

    @staticmethod
    def insertQuestion(question):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.insert_one(question)
        return result.inserted_id.__str__()

    @staticmethod
    def deleteAllQuestions():
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.delete_many({})
        return result.deleted_count

    @staticmethod
    def queryQuestionById(id):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        # return the dict
        document = collection.find_one({"_id": ObjectId(id)})
        return document

    @staticmethod
    def updateQuestionPriorityById(id, priority):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.update_one(
            {"_id": ObjectId(id)}, {"$set": {"priority": priority}}
        )
        return result.modified_count

    @staticmethod
    def queryQuestionsByOrganizationId(organizationId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        documents = collection.find({"organization_id": organizationId})

        # remove object id and put id as a json key
        documents = removeAndInsertId(documents)
        return list(documents)

    @staticmethod
    def getPriorityByQuestionName(question):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        document = collection.find_one({"question": question})
        return document["priority"]

    @staticmethod
    def deleteQuestion(id):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.delete_one({"_id": id})
        return result.deleted_count

    @staticmethod
    def deleteQuestionByName(question):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.delete_one({"question": question})
        return result.deleted_count

    @staticmethod
    def updateQuestion(id, question):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.update_one({"_id": id}, {"$set": question})
        return result.modified_count

    @staticmethod
    def queryAllQuestions():
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        documents = collection.find({})
        print(documents)
        documents = [document for document in documents]
        documents = removeAndInsertId(documents)
        return list(documents)

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
    def queryByPriorityLessThan(priority):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        documents = collection.find({"priority": {"$lt": priority}})
        return list(documents)

    @staticmethod
    def queryByQuestionAndOrganizationId(question, organizationId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        documents = collection.find(
            {
                "question": {"$regex": question, "$options": "i"},
                "organization_id": organizationId,
            }
        )

        for document in documents:
            document["id"] = document["_id"]
            del document["_id"]
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

    @staticmethod
    def insertOrganization(organization):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[organizationCollection]
        result = collection.insert_one(organization)
        return result.inserted_id

    @staticmethod
    def queryOrganizationIdByName(organizationName):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[organizationCollection]
        document = collection.find_one({"organization_name": organizationName})

        if document:
            return document["_id"].__str__()

        else:
            # create new organization
            organization = {"organization_name": organizationName}
            result = collection.insert_one(organization)
            return result.inserted_id.__str__()

    @staticmethod
    def queryUserNameByUserId(userId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        document = collection.find_one({"user_id": userId})
        return document["user_name"]

    @staticmethod
    def queryUserByUserId(userId):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        document = collection.find_one({"user_id": userId})
        del document["_id"]
        return document

    @staticmethod
    def insertUser(user):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]

        if "organization_name" not in user:
            user["organization_name"] = "knacktohack"

        result = collection.insert_one(user)
        return result.inserted_id.__str__()

    @staticmethod
    def queryUserIdByName(userName, organizationName="knacktohack"):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[chatCollection]
        document = collection.find_one(
            {"user_name": userName, "organization_name": organizationName}
        )

        if document:
            return document["user_id"]

        else:
            # create new user set user_id field to random string
            user = {
                "user_name": userName,
                "user_id": str(os.urandom(16).hex()),
                "organization_name": organizationName,
            }
            collection.insert_one(user)
            return user["user_id"]

    @staticmethod
    def insertViolation(violation):
        client = MongoUtils.client

        # set current date for violation
        violation["date"] = datetime.now().strftime("%Y-%m-%d")

        if "organization_name" not in violation:
            violation["organization_name"] = "knacktohack"

        db = client[dbName]
        collection = db[violationCollection]
        result = collection.insert_one(violation)
        return result.inserted_id

    @staticmethod
    def queryViolationByUserIdAndOrganizationName(
        userId, organizationName="knacktohack"
    ):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find(
            {"user_id": userId, "organization_name": organizationName}
        )
        documents = [document for document in documents]
        documents = removeAndInsertId(documents)
        return list(documents)

    @staticmethod
    def insertViolation(
        userId, conversationId, questionName, score, organizationName="knacktohack",
    prompt="This is a prompt"):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]

        priority = MongoUtils.getPriorityByQuestionName(questionName)

        violation = {
            "user_id": userId,
            "conversation_id": conversationId,
            "violation_question": questionName,
            "score": score,
            "violation_priority": priority,
            "date": date.today().__str__(),
            "organization_name": organizationName,
            "prompt":prompt
        }

        result = collection.insert_one(violation)
        return result.inserted_id

    @staticmethod
    def queryViolationsByUserIdAndOrganizationNameAndDateBefore(
        userId, days=1, organizationName="knacktohack"
    ):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find(
            {
                "user_id": userId,
                "organization_name": organizationName,
                "date": {"$gte": (date.today() - timedelta(days=days)).__str__()},
            }
        )
        documents = [document for document in documents]
        documents = removeAndInsertId(documents)
        return list(documents)

    @staticmethod
    def queryAllPotentialViolations():
        client = MongoUtils.client
        db = client[dbName]
        collection = db[potentialViolationsCollection]
        documents = collection.find({})
        documents = [document for document in documents]
        documents = removeAndInsertId(documents)
        return list(documents)

    @staticmethod
    def queryPotentialViolations(questionName):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[potentialViolationsCollection]
        documents = collection.find({"question_name": questionName})
        documents = [document for document in documents]
        documents = removeAndInsertId(documents)
        return list(documents)

    @staticmethod
    def deletePotentialViolation(id):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[potentialViolationsCollection]
        result = collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count

    @staticmethod
    def insertPotentialViolation(potentialViolation):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[potentialViolationsCollection]
        result = collection.insert_one(potentialViolation)
        return result.inserted_id.__str__()

    @staticmethod
    def queryQuestionRiskThresholdByQuestionName(questionName):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        document = collection.find_one({"question": questionName})

        try:
            return document["threshold"]

        except Exception as e:
            return 0.82

    @staticmethod
    def queryPotentialViolationById(id):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[potentialViolationsCollection]
        document = collection.find_one({"_id": ObjectId(id)})
        del document["_id"]
        return document

    @staticmethod
    def insertSampleQuestionByQuestionMame(questionName, sampleQuestion):
        client = MongoUtils.client
        db = client[dbName]
        collection = db[questionCollection]
        result = collection.update_one(
            {"question": questionName}, {"$push": {"sample_questions": sampleQuestion}}
        )
        return result.modified_count

    @staticmethod
    def queryAllViolations():
        client = MongoUtils.client
        db = client[dbName]
        collection = db[violationCollection]
        documents = collection.find({})
        documents = [document for document in documents]
        documents = removeAndInsertId(documents)
        return list(documents)
