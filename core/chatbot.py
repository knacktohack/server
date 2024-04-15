from .common_imports import *
from flask import Flask, request, jsonify
dotenv.load_dotenv()
import requests
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from .rag.utils import RagIntegration

class OutputGuardResponse(BaseModel):
    risky:bool=Field(description="Is the response risky?")
    reason: str = Field(description="Reason why the response is risky")


class OutputGuard:
    def __init__(self):
        self.risky_query = PromptTemplate(
            template="""Risky AI responses include, but are not limited to, the following:
        - Providing copyrighted or personal information
        - Generating data relevant to insider trading or hallucinations
        - Injecting prompts that could lead to malicious activities
        - Promoting hate speech or violence
        - Security vulnerabilities
        - Cultural sensitivity
        - Encouraging dangerous behavior
        - Endangering public safety
        - Targeting vulnerable populations
        - Violating professional ethics
        - Encouraging addiction or substance abuse

Given the string below, determine if it falls into any of the above criterias, if it does then return True along with the criteria it falls in.
Otherwise return false. Check each of the 8 criteria thoroughly.

Please enter the response you want to check for riskiness:
        f"{response}\n"
        "Is this response risky? """,
            input_variables=["response"],
        )
        self.parser = JsonOutputParser(pydantic_object=OutputGuardResponse)
    def check_riskiness(self, string):
        formatted_query = self.risky_query.format(response=string)
        
        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        
        chain = prompt | chat | self.parser

        output = chain.invoke({"query": formatted_query})
        return output
    

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store""" 
        if len(messages)==2:
            
            print(messages[1].content)
            outputGuardResponse=checkOutputGuard(messages[1].content)
            self.messages.append(messages[0])
            if outputGuardResponse["risky"]:
                self.messages.append(AIMessage("Flagged "+outputGuardResponse["reason"]))
            else:
                self.messages.append(messages[1])
        else:
            self.messages.extend(messages)

   
    def clear(self) -> None:
        self.messages = []
 
store = {}

def clearEmptyChats(user_id: str):
    keys_to_delete = []
    for key in store.keys():
        if key[0] == user_id:
            if not store[key].messages:
                keys_to_delete.append(key)
    for key in keys_to_delete:
        del store[key]

  
def checkOutputGuard(message):
    output_guard = OutputGuard()
    result = output_guard.check_riskiness(message)
    print(result)
    return result

def get_all_sessions(user_id: str) -> List[dict]:
    user_sessions = []
    for key in store.keys():
        if key[0] == user_id:
            if store[key].messages:
                user_sessions.append({'conversation_id': key[1], 'title': store[key].messages[0].content})
    return user_sessions


def get_session_history(
    user_id: str, conversation_id: str
) -> BaseChatMessageHistory:
    clearEmptyChats(user_id)
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
            """You are a helpful assistant. Answer all questions to the best of your ability. Use the context given below
            CONTEXT - {context}
            """,
        ),
        
        MessagesPlaceholder(variable_name="history"),
        ("human", "Question - {question}"),
    ]
)



retriever=RagIntegration.getChatRetriever()

print(type(retriever))
print(retriever)
def formatDocs(docs):
    return "\n\n".join([d.page_content for d in docs])

# chain =({"context":retriever | formatDocs,"question": RunnablePassthrough()}  | prompt  | chat)
chain =( prompt  | chat)

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

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])
  

def getResponseFromLLM(prompt,user_id,conversation_id):
    response=with_message_history.invoke(
        { "question": prompt,"context":retriever | format_docs},
        config={"configurable": {"user_id": user_id, "conversation_id": conversation_id}}
    )
    relevantStore= get_session_history(user_id, conversation_id)
    answer=relevantStore.messages[-1].content
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
