from .common_imports import *
from flask import Flask, request, jsonify
dotenv.load_dotenv()
import requests
chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
app = Flask(__name__)
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        if len(messages)==2:
            outputGuardResponse=checkOutputGuard(messages[1].content)
            self.messages.append(messages[0])
            if outputGuardResponse!="safe":
                self.messages.append(AIMessage("Flagged "+"flagging reason"))
            else:
                self.messages.append(messages[1])
        else:
            self.messages.extend(messages)

 
    def clear(self) -> None:
        self.messages = []
 
store = {}



def checkOutputGuard(message):
    return "safe"

def get_all_sessions(user_id: str) -> List[BaseChatMessageHistory]:
    user_sessions = []
    for key in store.keys():
        if key[0] == user_id:
            user_sessions.append((key[1],store[key]))
    return user_sessions


def get_session_history(
    user_id: str, conversation_id: str
) -> BaseChatMessageHistory:
    if (user_id, conversation_id) not in store:
        store[(user_id, conversation_id)] = InMemoryHistory()
    return store[(user_id, conversation_id)]

def session_history_exists(
    user_id: str, conversation_id: str
) -> BaseChatMessageHistory:
    if (user_id, conversation_id) not in store:
        return False
    return True
 

def format_session_messages(chat_history_messages):
    #takes in a list
    #this will be a list of dictionary, each item will have a type and a content field
    messages=[]
    for message in chat_history_messages:
        if(message.type=="human"):
            messages.append({"type":"human","content":message.content})
        else:
            messages.append({"type":"ai","content":message.content})
    return messages

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)




chain = prompt | chat

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="history",
    history_factory_config=[
        ConfigurableFieldSpec(
            id="user_id",
            annotation=str,
            name="User ID",
            description="Unique identifier for the user.",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="conversation_id",
            annotation=str,
            name="Conversation ID",
            description="Unique identifier for the conversation.",
            default="",
            is_shared=True,
        ),
    ],
)


  

def getResponseFromLLM(prompt,user_id,conversation_id):
    response=with_message_history.invoke(
        { "question": prompt},
        config={"configurable": {"user_id": user_id, "conversation_id": conversation_id}}
    )
    relevantStore= get_session_history(user_id, conversation_id)
    answer=relevantStore.messages[-1].content
    # print("-----------relevantStore-=---------")
    # print(relevantStore.messages[-1].content)
    # print("-----------relevantStoreend-=---------")
    if answer.split(" ")[0]=="Flagged":
        return answer,400
    else:
        return answer,200
 
     
   


 
# @app.route("/generate", methods=["POST"])
# def generate_text():
#     prompt = request.get_json()["prompt"]
#     user_id = request.get_json()["user_id"]  # Get user ID from request
#     # print(type(prompt))
#     conversation_id=request.get_json()["conversation_id"]
#     response=with_message_history.invoke(
#     { "question": prompt},
#     config={"configurable": {"user_id": user_id, "conversation_id": conversation_id}}
# )
#     relevantStore=store[(user_id, conversation_id)]
#     print(relevantStore)
#     print()
#     return jsonify({"response": response.content, "history": "chat_history"})


# @app.route("/<user_id>/<conversation_id>", methods=["GET"])
# def get_text(user_id,conversation_id):
#     try: 
        
#         if user_id is None or conversation_id is None:
#             return jsonify({"error": "Missing user_id or conversation_id"}), 400
#         chat_history = get_session_history(user_id, conversation_id)
#         formatted_messages=format_session_messages(chat_history.messages)
#         response = {"response": formatted_messages}
#         return jsonify(response)
     
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)