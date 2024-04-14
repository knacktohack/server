import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from ..rag.utils import RagIntegration
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field

load_dotenv()

openApiKey = os.getenv("OPENAI_API_KEY")

class Output(BaseModel):
    priority: int = Field(description="How severe is the violation of the question on a range of 1 to 10")
    questions: list[str] = Field(description="The questions generated by the model")

class QuestionGenerator:
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=openApiKey,
    )
    
    template = PromptTemplate(template = """
        You are given a question template, that is a superset of a class of questions that can be asked.
        You job is to generate 5 different ways that a user might ask a question that fits into this category.
        The template references some activity, and the user is asking a question about PERFORMING that activity.
        Consider cases where the user may ask an INDIRECT question.
        Consider ALL ASPECTS of how the user perform this activity.
        Avoid generating REPETITIVE questions.
        The generated questions should appear NATURAL. Output each of the generated questions on a NEW LINE.
        Do not include any additional information.
        Use the following context
        
        CONTEXT - {context}
        
        QUESTION - {original_question}
    """,
       input_variables=["original_question"])
    
    
    retriever = RagIntegration.getRetriever()
    
    parser = StrOutputParser()
    
    @staticmethod
    def generateQuestions(original_question: str,context=True):
        # filled_template = QuestionGenerator.template.format(original_question=original_question)
        
        if context:
            chain = (
                {"context":QuestionGenerator.retriever, "original_question":RunnablePassthrough()}
                | QuestionGenerator.template
                | QuestionGenerator.llm
                | QuestionGenerator.parser
            )    
            
            output = chain.invoke(original_question)
        else:
            chain = (
                QuestionGenerator.template
                | QuestionGenerator.llm
                | QuestionGenerator.parser
            )
            
            output = chain.invoke({
                "context": "",
                "original_question": original_question
            })
        
        #split by newlines
        output = output.split("\n")
        
        #remove initial numbering
        output = [x[3:] for x in output]
        return output