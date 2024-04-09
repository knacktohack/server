from ..kors.question_extractor import QuestionExtractor
from ..question_generation.question_generator import QuestionGenerator
from ..semantic_router.utils import insertRoute


def processChunk(chunk: str):
    questions = QuestionExtractor.extractQuestions(chunk)
    for question in questions['question_parser']['question']:
        generatedQuestions = QuestionGenerator.generateQuestions(question)
        insertRoute(question,generatedQuestions)
    return questions