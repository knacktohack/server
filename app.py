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
from core.azure.blob_storage import uploadToBlobStorage
from pymongo import MongoClient
load_dotenv()
app = Flask(__name__)
# app.config["MONGO_CLIENT"] = MongoClient(os.getenv("MONGO_URL"))
mongo_client = MongoClient(os.getenv("MONGO_URL"))
# app.config["MONGO_DB"] = app.config["MONGO_CLIENT"].knacktohack
mongo_db = mongo_client.knacktohack

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

@app.route("/upload", methods=["POST"])
def uploadFileToBlobStorage():
    try:
        # Get uploaded file from form data
        uploadedFile = request.files.get("file")
        if not uploadedFile:
            return jsonify({"message": "No file uploaded"}), 400

        # Get filename and data
        fileName = uploadedFile.filename
        fileData = uploadedFile.read()

        # Call the upload function
        uploadToBlobStorage(fileData, fileName)

        return jsonify({"message": f"Successfully uploaded {fileName} to Azure Blob Storage"})
    except Exception as e:
        print(e)
        return jsonify({"message": "There was an error uploading the file"}), 500


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
def get_question(question_id, organization_id):
    try: 
        questions = mongo_db.questions
        if question_id:
            res = questions.find_one({"_id":question_id})
            return jsonify({"data": res})
        res = questions.find({})
        return jsonify({"data": res})
        # if organization_id:
        #     res = questions.find({"organization_id"})
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/questions/new", methods=["POST"])
def get_question():
    try: 
        questions = mongo_db.questions
        question = {
            "question": request.get_json()["question"],
            "organization": request.get_json()["organization"],
            "priority": request.get_json()["priority"] if request.get_json()["priority"] else 0
        }
        questions.insert_one(question)
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/questions/<id>", methods=["POST", "PUT", "PATCH"])
def update_question(id):
    try: 
        questions = mongo_db.questions
        new_question = {
            "question": request.get_json()["question"],
            "organization": request.get_json()["organization"],
            "priority": request.get_json()["priority"] if request.get_json()["priority"] else 0
        }
        questions.find_one_and_update({"_id":id}, {"$set": new_question})
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/questions/<id>", methods=["DELETE"])
def delete_question(id):
    try: 
        questions = mongo_db.questions
        questions.find_one_and_delete({"_id":id})
     
    except Exception as e:
        return jsonify({"error": str(e)}), 500




def startApp():
    app.run(port=8000)

if __name__ == "__main__":
    app.run(port=8000)
