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
from core.chatbot import get_session_history, format_session_messages,get_all_sessions,with_message_history,getResponseFromLLM 
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from core.azure.blob_storage import uploadToBlobStorage,getAllFilesByOrganizationId
from pymongo import MongoClient
from core.mongo.utils import MongoUtils
from core.integration.pinecone_integration import PineConeIntegration
from core.MessageTypes import MessageTypes
from core.risk.utils import RiskIntegration
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
def uploadRulesToBlobStorage():
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
        uploadToBlobStorage(fileData, fileName,organizationId,type=MessageTypes.RULES)

        return jsonify({"message": f"Successfully uploaded {fileName} to Azure Blob Storage"})
    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error uploading the file"}), 500
    
    
@app.route("/upload_company_documents", methods=["POST"])
def uploadCompanyDataToBlobStorage():
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
        uploadToBlobStorage(fileData, fileName,organizationId,type=MessageTypes.DATA)

        return jsonify({"message": f"Successfully uploaded {fileName} to Azure Blob Storage"})
    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error uploading the file"}), 500
    
    
    
@app.route("/rules_files", methods=["POST"])
def getRulesFiles():
    try:
        organization = "knacktohack"
        #check request.body as json for organization
        body = request.get_json()
        print(body)
        if "organization" in body:
            organization = body["organization"]
            
        organizationId = MongoUtils.queryOrganizationIdByName(organization)
        print(organizationId)
        files = getAllFilesByOrganizationId(organizationId, MessageTypes.RULES)
        
        return jsonify(files)
    

    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error getting the files"}), 500
    
    
@app.route("/data_files", methods=["POST"])
def getCompanyFiles():
    try:
        organization = "knacktohack"
        #check request.body as json for organization
        body = request.get_json()
        print(body)
        if "organization" in body:
            organization = body["organization"]
            
        organizationId = MongoUtils.queryOrganizationIdByName(organization)
        print(organizationId)
        files = getAllFilesByOrganizationId(organizationId, MessageTypes.DATA)
        
        return jsonify(files)
    

    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error getting the files"}), 500
        
        
@app.route("/questions_delete",methods=['POST'])
def delete_question():
    try:
        body = request.get_json()
        question = body["question"]
        PineConeIntegration.deleteRoute(question)
        return jsonify({"message": "Successfully deleted question"}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        


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
    conversation_id=request.get_json()["conversation_id"]
    print(type(prompt))
    # questionName,questionScore=PineConeIntegration.getRoute(prompt)
    questionName="temp"
    flag=False#RiskIntegration.persistRisk(user_id,conversation_id,questionName,questionScore,prompt)
    if flag:
        session=get_session_history(user_id,conversation_id)
        session.add_user_message(prompt)
        session.add_ai_message(questionName+"flagged")
        return jsonify({"response": "Sorry this question is blocked as I cannot answer "+questionName, "history": "chat_history","status":400})
        
    else:
        response,status=getResponseFromLLM(prompt,user_id,conversation_id)
        return jsonify({"response": response, "history": "chat_history","status":status})
    
    
@app.route("/get_violations", methods=["GET"])
def get_violations():
    try:
        violations = MongoUtils.queryAllViolations()
        return jsonify(violations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/sample_question",methods=["POST"])
def insert_sample_question():
    try:
        body = request.get_json()
        question = body["question"]
        sample_question = body['sample_question']
        
        PineConeIntegration.insertRoute(question,[sample_question])
        return jsonify({"message": "Successfully added question"}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history/<user_id>", methods=["GET"])
def get_sessions(user_id):
    try: 
        
        if user_id is None :
            return jsonify({"error": "Missing user_id"}), 400
        sessions = get_all_sessions(user_id)
        response = {"response": sessions}
        return jsonify(response)
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/history/<user_id>/<conversation_id>", methods=["GET"])
def get_text(user_id,conversation_id):
    try: 
        
        if user_id is None or conversation_id is None:
            return jsonify({"error": "Missing user_id or conversation_id"}), 400
        chat_history = get_session_history(user_id, conversation_id)
        formatted_messages=format_session_messages(chat_history.messages)
        response = {"response": formatted_messages}
        print(chat_history.messages)
        return jsonify(response)
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/insert_question_sample",methods=["POST"])
def insert_question_sample():
    try:
        questionId = request.get_json()["id"]
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/questions", methods=["POST"])
def get_question():
    try: 
        body  = request.get_json()
        
        questions = []
        
        if "organization" in body:
            organizationName = body["organization"]
            organizationId = MongoUtils.queryOrganizationIdByName(organizationName)
            questions = MongoUtils.queryQuestionsByOrganizationId(organizationId)
            
        else:
            questions = MongoUtils.queryAllQuestions()
            
        return jsonify(questions)
     
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
    
@app.route("/questions_update", methods=["PUT", "PATCH"])
def update_question():
    try:
        body = request.get_json()
        id  = body["id"]
        MongoUtils.updateQuestionPriorityById(id, body["priority"])
        
        return jsonify({"message": f"Updated record"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/rules_add", methods=["POST"])
def add_question():
    try:
        body = request.get_json()
        question = body["rule"]
        print(question)
        questions = PineConeIntegration.processChunk(question)
    
        return jsonify(questions)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
     
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

# @app.route("/questions/<id>", methods=["DELETE"])
# def delete_question():
#     try: 
#         id = request.get_json()["id"]
#         cnt = MongoUtils.deleteQuestion(id)
        
#         return jsonify({"message": f"Deleted {cnt} record"})
     
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

'''
    send body as
    {
        "question": "question"
    }
    
    or an empty body for no question specific filtering
'''
@app.route("/potential_violations", methods=["POST"])
def get_potential_violations():
    try:
        body = request.get_json()
        
        if 'question' not in body:
            return jsonify(MongoUtils.queryAllPotentialViolations())
        
        question = body["question"]
        
        return jsonify(MongoUtils.queryPotentialViolations(question))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
'''
    send body as
    {
        "id": id of the potential violation,
        "accepted": "true" or "false"
    }
'''
    
@app.route("/handle_potential_violation", methods=["POST"])
def handle_potential_violation():
    try:
        body = request.get_json()
        id = body["id"]
        potentialViolation = MongoUtils.queryPotentialViolationById(id)
        accepted = body["accepted"]
        
        if accepted=="true":
            PineConeIntegration.handlePotentialViolation(potentialViolation,id,accepted=True)
        else:
            PineConeIntegration.handlePotentialViolation(potentialViolation,id,accepted=False)
            
        return jsonify({"message": "Handled potential violation"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        
@app.route("/get_risk", methods=["GET"])
def get_risk():
    # try:
    return jsonify(MongoUtils.queryUserIdAndSeverityScoreDescending())
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500
        

def startApp():
    app.run(port=8000)

if __name__ == "__main__":
    app.run(port=8000,debug=True)
