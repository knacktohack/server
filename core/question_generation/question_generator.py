import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from ..rag.utils import RagIntegration
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

openApiKey = os.getenv("OPENAI_API_KEY")

class QuestionGenerator:
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=openApiKey,
    )
    
    template = PromptTemplate(template = """
        You are given a question template, that is a superset of a class of questions that cen be asked.
        You job is to generate 3 different ways that a user might ask a question that fits into this category.
        The template references some activity, and the user is asking a question about performing that activity.
        Consider cases where the user may ask an INDIRECT question, or ask the question in a different way.
        Consider ALL ASPECTS of how the user may ask a question.
        Generate a DIFFERENT question each time. Avoid generating REPETITIVE questions.
        The generated questions should appear NATURAL. Output each of the generated questions on a new line. Do not include any additional information.
        Use the following context
        
        Context - {context}
        
        Question - {original_question}
    """,
       input_variables=["original_question"])
    
    
    retriever = RagIntegration.getRetriever()
    
    parser = StrOutputParser()
    
    @staticmethod
    def generateQuestions(original_question: str):
        # filled_template = QuestionGenerator.template.format(original_question=original_question)    
        chain = (
            {"context":QuestionGenerator.retriever, "original_question":RunnablePassthrough()}
            | QuestionGenerator.template
            | QuestionGenerator.llm
            | QuestionGenerator.parser
        )
        output = chain.invoke(original_question)
        
        #split by newlines
        output = output.split("\n")
        
        #remove initial numbering
        output = [x[3:] for x in output]
        return output