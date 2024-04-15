from ..kors.question_extractor import QuestionExtractor
from ..question_generation.question_generator import QuestionGenerator
from ..semantic_router.utils import insertRoute, deleteAll, deleteRoute
from ..semantic_router.create_index import createIndex, returnIndex
import os
from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer, Route
from dotenv import load_dotenv
from ..pinecone.question_utils import PineconeClient
from ..mongo.utils import MongoUtils

load_dotenv()


encoder = OpenAIEncoder(openai_api_key=os.getenv("OPENAI_API_KEY"))


class PineConeIntegration:
    index = returnIndex()

    # routes_dict = {}
    # for route, utterance in index.get_routes():
    #     if route not in routes_dict:
    #         routes_dict[route] = []
    #     routes_dict[route].append(utterance)

    # routes = [
    #     Route(name=route, utterances=utterances)
    #     for route, utterances in routes_dict.items()
    # ]

    routeLayer = None  # RouteLayer(routes=routes,encoder=encoder,index=index)

    @staticmethod
    def generateRouteLayer():
        routes_dict = {}
        for route, utterance in PineConeIntegration.index.get_routes():
            if route not in routes_dict:
                routes_dict[route] = []
            routes_dict[route].append(utterance)

        # print(routes_dict)
        routes = [
            Route(name=route, utterances=utterances)
            for route, utterances in routes_dict.items()
        ]

        routeLayer = RouteLayer(
            routes=routes, encoder=encoder, index=PineConeIntegration.index
        )
        return routeLayer

    @staticmethod
    def processChunk(chunk: str, organizationId="661a47db428c4cd50785b191"):
        print(chunk)
        questions = QuestionExtractor.extractQuestions(chunk)
        print(questions)
        returnQuestions = []

        if len(questions.keys()) == 0:
            return []
        if len(questions["question_parser"]) == 0:
            return []

        for question in questions["question_parser"][0]["listElement"]:
            vector = encoder(question["question"])[0]
            similarDataScore = PineconeClient.findSimilarVector(vector)

            if similarDataScore < 0.90:
                print(question)
                generatedQuestions = QuestionGenerator.generateQuestions(
                    question["question"]
                )
                returnId = MongoUtils.insertQuestion(
                    {
                        "question": question["question"],
                        "organization_id": organizationId,
                        "priority": question["priority"],
                        "sample_questions": generatedQuestions,
                    }
                )

                returnQuestions.append(
                    {
                        "question": question["question"],
                        "organization_id": organizationId,
                        "priority": question["priority"],
                        "sample_questions": generatedQuestions,
                        "id": returnId
                    }
                )
                print(generatedQuestions)
                insertRoute(question["question"], generatedQuestions)
                PineconeClient.insertData(
                    [{"question": question["question"], "vector": vector}]
                )
        print(returnQuestions)
        return returnQuestions

    @staticmethod
    def deleteAll():
        return deleteAll()

    @staticmethod
    def getRoute(text: str):
        if PineConeIntegration.routeLayer is None:
            PineConeIntegration.routeLayer = RouteLayer.from_json("route_layer.json")#PineConeIntegration.generateRouteLayer()
            # PineConeIntegration.routeLayer.to_json("route_layer.json")
        vector = PineConeIntegration.routeLayer._encode(text)
        route, score = PineConeIntegration.routeLayer._retrieve_top_route(vector=vector)
        
        if route  is None:
            return "No Route Found", 0
        return route.name, max(score)

    @staticmethod
    def insertRoute(routeName, utterances):
        insertRoute(routeName, utterances)
        PineConeIntegration.routeLayer = PineConeIntegration.generateRouteLayer()

    @staticmethod
    def deleteRoute(routeName):
        MongoUtils.deleteQuestionByName(routeName)
        PineconeClient.deleteQuestion(routeName)
        return deleteRoute(routeName)
    
    @staticmethod
    def handlePotentialViolation(potentialViolation,id,accepted=False):
        if accepted:
            insertRoute(potentialViolation["question_name"],[potentialViolation["prompt"]])
            MongoUtils.insertSampleQuestionByQuestionMame(potentialViolation["question_name"],potentialViolation["prompt"])
        else:
            pass
        
        MongoUtils.deletePotentialViolation(id)
        return
        
