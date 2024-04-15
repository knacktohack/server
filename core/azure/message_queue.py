from azure.eventhub import EventHubProducerClient, EventData
from azure.servicebus import ServiceBusClient
import os
from dotenv import load_dotenv
import time
import json
from ..MessageTypes import MessageTypes
from ..chunker import getChunksFromFiles
from ..integration.pinecone_integration import PineConeIntegration
from ..rag.utils import RagIntegration

load_dotenv()
queueConnectionString = os.getenv("AZUE_QUEUE_CONNECTION_STRING")
chunkingQueueName = os.getenv("AZURE_CHUNKING_QUEUE_NAME")
fullyQualifiedNamespace = os.getenv("AZURE_FULLY_QUALIFIED_NAMESPACE")
azureKey = os.getenv("AZURE_QUEUE_KEY")
azureValue = os.getenv("AZURE_KEY_VALUE")


def publishToServiceBusQueue(
    connectionString, queueName, message
) -> None:
    """
    Publish a message to an Azure Service Bus Queue.

    Args:
        connectionString (str): The Azure Service Bus connection string.
        queueName (str): The name of the queue to publish to.
        message (str): The message content to be published.
    """
    producer = EventHubProducerClient.from_connection_string(
        conn_str=connectionString, eventhub_name=queueName
    )
    
    if(isinstance(message,dict)):
        message = json.dumps(message)
        
    eventDataBatch = producer.create_batch()
    eventDataBatch.add(EventData(message))
    producer.send_batch(eventDataBatch)
    print(f"Message sent to queue: {queueName}")


def publishToChunkingQueue(message: str) -> None:
    """
    Publish a message to the Azure Chunking Queue.

    Args:
        message (str): The message content to be published.
    """
    publishToServiceBusQueue(queueConnectionString, chunkingQueueName, message)


def pollQueue(queueName, maxMessages: int = 10, deleteMessage: bool = False) -> list:
    serviceBusClient = ServiceBusClient.from_connection_string(conn_str=queueConnectionString)
    receiver = serviceBusClient.get_queue_receiver(queue_name=queueName, max_wait_time=5)

    messagesArray = []

    with serviceBusClient:
        with receiver:
            messages = receiver.receive_messages(max_message_count=maxMessages)
            for message in messages:
                body=""
                for b in message.body:
                    body+=b.decode("utf-8")
                messageBody = body
                
                try:
                    jsonBody = json.loads(messageBody)
                except:
                    jsonBody = messageBody
                messagesArray.append(jsonBody)
                
                
                if deleteMessage:
                    receiver.complete_message(message)
    return messagesArray


def loop(queueName, callback=print,timeInMinutes: int = 0.1,maxMessages=10,deleteMessage=False) -> None:
    while True:
        messages = pollQueue(queueName,maxMessages=maxMessages,deleteMessage=deleteMessage)
        callback(messages)
        time.sleep(timeInMinutes * 60)
    


def loopForChunkingQueue(timeInMinutes: int = 2,deleteMessage=True) -> None:
    """
    Continuously polls the Azure Chunking Queue at a specified interval.

    Args:
        timeInMinutes (int, optional): The interval between polls in minutes. Defaults to 10.
        **kwargs: Additional arguments passed to pollForMessages function.
    """
    
    def callback(messages):
        print(messages)
        for message in messages:
            if message['type'] == MessageTypes.RULES:
                chunks = getChunksFromFiles(message['url'],chunk_size=1000)
                for chunk in chunks['chunks']:
                    PineConeIntegration.processChunk(chunk)
                    
            elif message['type'] == MessageTypes.DATA:
                chunks = getChunksFromFiles(message['url'],chunk_size=500)
                for chunk in chunks['chunks']:
                    RagIntegration.addText(chunk)
                
    loop(queueName=chunkingQueueName, timeInMinutes=timeInMinutes, deleteMessage=deleteMessage, callback=callback)
