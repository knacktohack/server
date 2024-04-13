import os
# import requests
from pydantic import BaseModel
from typing import List
import uvicorn
import json
import signal
from dotenv import load_dotenv
import requests
from flask import jsonify
from core.chatbot import get_session_history, format_session_messages,with_message_history
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from core.azure.blob_storage import uploadToBlobStorage,getAllFilesByOrganizationId
from pymongo import MongoClient
from core.mongo.utils import MongoUtils
load_dotenv()
app = Flask(__name__)
# app.config["MONGO_CLIENT"] = MongoClient(os.getenv("MONGO_URL"))
# app.config["MONGO_DB"] = app.config["MONGO_CLIENT"].knacktohack

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

frontendPort = "http://localhost:3000"

CORS(app, resources={r"/*": {"origins": frontendPort}})

user_id = "12345"


@app.get("/")
async def ping():
    return {"message": "Server is Live"}

@app.route("/upload_rules", methods=["POST"])
def uploadFileToBlobStorage():
    try:
        # Get uploaded file from form data
        uploadedFile = request.files.get("file")
        organization = "knacktohack"
        if "organization" in request.form:
            organization = request.form.get("organization")
            print(organization)
            
        organizationId = MongoUtils.queryOrganizationIdByName(organization)
        print(organizationId)
        if not uploadedFile:
            return jsonify({"message": "No file uploaded"}), 400

        # Get filename and data
        fileName = uploadedFile.filename
        fileData = uploadedFile.read()

        # Call the upload function
        uploadToBlobStorage(fileData, fileName,organizationId,type="rules_upload")

        return jsonify({"message": f"Successfully uploaded {fileName} to Azure Blob Storage"})
    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error uploading the file"}), 500
    
    
@app.route("/upload_company_documents", methods=["POST"])
def uploadFileToBlobStorage():
    try:
        # Get uploaded file from form data
        uploadedFile = request.files.get("file")
        organization = "knacktohack"
        if "organization" in request.form:
            organization = request.form.get("organization")
            print(organization)
            
        organizationId = MongoUtils.queryOrganizationIdByName(organization)
        print(organizationId)
        if not uploadedFile:
            return jsonify({"message": "No file uploaded"}), 400

        # Get filename and data
        fileName = uploadedFile.filename
        fileData = uploadedFile.read()

        # Call the upload function
        uploadToBlobStorage(fileData, fileName,organizationId,type="company_documents_upload")

        return jsonify({"message": f"Successfully uploaded {fileName} to Azure Blob Storage"})
    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error uploading the file"}), 500
    
    
    
@app.route("/files", methods=["POST"])
def getFiles():
    try:
        organization = "knacktohack"
        #check request.body as json for organization
        body = request.get_json()
        print(body)
        if "organization" in body:
            organization = body["organization"]
            
        organizationId = MongoUtils.queryOrganizationIdByName(organization)
        print(organizationId)
        files = getAllFilesByOrganizationId(organizationId)
        
        return jsonify(files)
    

    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error getting the files"}), 500
        
        


@app.get("/query")
async def query(q: str):
    print(q)

    # semantic router

    # openai

    # gaurd rails

    return {"message": "success"}


@app.route("/generate", methods=["POST"])
def generate_text():
    prompt = request.get_json()["prompt"]
    user_id = request.get_json()["user_id"]  # Get user ID from request
    print(type(prompt))
    conversation_id=request.get_json()["conversation_id"]
    response=with_message_history.invoke(
    { "question": prompt},
    config={"configurable": {"user_id": user_id, "conversation_id": conversation_id}}
)
    # print(store)
    return jsonify({"response": response.content, "history": "chat_history"})


@app.route("/<user_id>/<conversation_id>", methods=["GET"])
def get_text(user_id,conversation_id):
    try: 
        
        if user_id is None or conversation_id is None:
            return jsonify({"error": "Missing user_id or conversation_id"}), 400
        chat_history = get_session_history(user_id, conversation_id)
        formatted_messages=format_session_messages(chat_history.messages)
        response = {"response": formatted_messages}
        return jsonify(response)
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/questions", methods=["GET"])
def get_question(question, organizationName):
    try: 
        organizationId = MongoUtils.queryOrganizationIdByName(organizationName)
        res = MongoUtils.queryByQuestionAndOrganizationId(question, organizationId)
        return jsonify(res)
        # if organization_id:
        #     res = questions.find({"organization_id"})
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/questions/new", methods=["POST"])
def insert_question():
    try: 
        body = request.get_json()
        organizationName = body["organization"]
        organizationId = MongoUtils.queryOrganizationIdByName(organizationName)
        
        question = {
            "question": body["question"],
            "organization_id": organizationId,
            "priority": body["priority"] if body["priority"] else 0
        }
        
        MongoUtils.insertQuestion(question)
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/questions/<id>", methods=["POST", "PUT", "PATCH"])
def update_question():
    try:
        body = request.get_json()
        id  = body["id"]
        
        oldQuestion = MongoUtils.queryQuestionById(id)
        
        question = {
            "question": body["question"] if body["question"] else oldQuestion["question"],
            "organization_id": body["organization_id"] if body["organization_id"] else oldQuestion["organization_id"],
            "priority": body["priority"] if body["priority"] else oldQuestion["priority"]
        }
        
        cnt = MongoUtils.updateQuestion(id, question)
        
        return jsonify({"message": f"Updated {cnt} record"})
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/questions/<id>", methods=["DELETE"])
def delete_question():
    try: 
        id = request.get_json()["id"]
        cnt = MongoUtils.deleteQuestion(id)
        
        return jsonify({"message": f"Deleted {cnt} record"})
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500




def startApp():
    app.run(port=8000)

if __name__ == "__main__":
    app.run(port=8000)
