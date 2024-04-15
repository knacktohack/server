from typing import List, Optional
import os
from langchain.chat_models import ChatOpenAI
from kor.extraction import create_extraction_chain
from kor.nodes import Object, Text, Number

from kor import extract_from_documents, from_pydantic, create_extraction_chain


from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .schema import schema
from dotenv import load_dotenv

load_dotenv()

openApiKey = os.getenv("OPENAI_API_KEY")

class QuestionExtractor:
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=openApiKey,
        max_tokens=1000,
    )
    
    chain = create_extraction_chain(llm, schema,encoder_or_encoder_class="JSON",input_formatter=None)
    
    @staticmethod
    def extractQuestions(text: str):
        return QuestionExtractor.chain.predict(text = text)['data']

