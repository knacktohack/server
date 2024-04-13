import os
import pinecone
from pinecone import PodSpec
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

indexName = os.getenv("QUESTION_INDEX_NAME")


class PineconeClient:
    _client = None
    _api_key = os.getenv("QUESTION_INDEX_API_KEY")

    @staticmethod
    def _get_client():
        if not PineconeClient._client and PineconeClient._api_key:
            PineconeClient._client = pinecone.Pinecone(api_key=PineconeClient._api_key)
        elif not PineconeClient._api_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set.")
        return PineconeClient._client

    @staticmethod
    def insertQuestion(questionVector):
        PineconeClient._get_client()
        PineconeClient.insertData(
            [
                {
                    "question": questionVector["question"],
                    "vector": questionVector["vector"],
                }
            ]
        )

    @staticmethod
    def createIndex(dimension=1536, metric="cosine"):
        """
        Create a new index.

        Args:
        - name (str): Name of the index to be created.
        - dimension (int): Dimension of the vectors.
        - metric (str): Similarity metric to be used.

        Returns:
        - None
        """
        PineconeClient._get_client()
        PineconeClient._client.create_index(
            name=indexName,
            dimension=dimension,
            metric=metric,
            spec=PodSpec(environment="us-west1-gcp", pod_type="p1.x1", pods=1),
        )

    @staticmethod
    def insertData(data):
        """
        Insert vectors and questions into an index.

        Args:
        - indexName (str): Name of the index to insert vectors into.
        - data (List[Dict[str, Union[str, List[float]]]]): List of dictionaries containing "question" and "vector" keys.

        Returns:
        - None
        """
        PineconeClient._get_client()
        index = PineconeClient._client.Index(indexName)

        records = []

        for record in data:
            records.append(
                {
                    "id": record["question"],
                    "values": record["vector"],
                    "metadata": {"question": record["question"]},
                }
            )
        index.upsert(vectors=records)

    @staticmethod
    def findSimilarVector(vector, topK=1):
        """
        Find the most similar vector to the given vector in the index.

        Args:
        - indexName (str): Name of the index to search.
        - vector (List[float]): Vector for which to find the most similar vector.
        - topK (int): Number of most similar vectors to return.

        Returns:
        - List[Tuple[str, float]]: List of tuples containing ID and similarity score.
        """
        try:
            PineconeClient._get_client()
            index = PineconeClient._client.Index(indexName)
            results = index.query(vector=vector, top_k=topK)
            return results["matches"][0]["score"]
        except:
            return 0.0

    @staticmethod
    def deleteAll():
        # just delete all data from index
        PineconeClient._get_client()
        PineconeClient._client.delete_index(indexName)
