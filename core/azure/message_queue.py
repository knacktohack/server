from azure.eventhub import EventHubProducerClient, EventData, EventHubConsumerClient, PartitionContext,EventHubSharedKeyCredential
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()
queueConnectionString = os.getenv("AZUE_QUEUE_CONNECTION_STRING")
chunkingQueueName = os.getenv("AZURE_CHUNKING_QUEUE_NAME")
fullyQualifiedNamespace = os.getenv("AZURE_FULLY_QUALIFIED_NAMESPACE")
azureKey = os.getenv("AZURE_QUEUE_KEY")
azureValue = os.getenv("AZURE_KEY_VALUE")


def publishToServiceBusQueue(
    connectionString: str, queueName: str, message: str
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
    print(producer)
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


def pollForMessages(
    queueName: str,
    consumerGroup: str = "$default",
    maxMessages: int = 1,
    callback=print,
    delete: bool = True,
) -> None:
    """
    Polls for messages from an Azure Service Bus Queue (Event Hub).

    Args:
        queueName (str): The name of the queue (Event Hub) to listen to.
        consumerGroup (str, optional): The consumer group to use. Defaults to "$default".
        maxMessages (int, optional): The maximum number of messages to receive per poll. Defaults to 1.
        callback (callable, optional): The function to call with processed messages. Defaults to print.
        delete (bool, optional): Whether to acknowledge received messages (similar to SQS deletion). Defaults to True.
    """

    if not queueConnectionString:
        raise ValueError("Missing environment variable: SERVICE_BUS_CONNECTION_STRING")
    

    credential = EventHubSharedKeyCredential(azureKey, azureValue)
    client = EventHubConsumerClient(
        eventhub_name=queueName,
        consumer_group=consumerGroup,
        fully_qualified_namespace=fullyQualifiedNamespace,
        credential=credential,
        max_batch_size=maxMessages
    )

    def onEventReceived(partitionContext: PartitionContext,eventData: EventData) -> None:
        processedMessages = []
        for message in json.loads(eventData.body.decode("utf-8")):
            processedMessages.append(message)
        callback(processedMessages)

        # Acknowledge the received message (similar to SQS deletion)
        if delete:
            partitionContext.update_checkpoint(eventData)

    try:
        with client:
            client.receive(
                on_event=onEventReceived
            )
    except KeyboardInterrupt:
        print("Stopped polling due to keyboard interrupt.")


def loopForMessages(queueName: str, timeInMinutes: int = 0.1, **kwargs) -> None:
    """
    Continuously polls an Azure Service Bus Queue (Event Hub) at a specified interval.

    Args:
        queueName (str): The name of the queue (Event Hub) to listen to.
        timeInMinutes (int, optional): The interval between polls in minutes. Defaults to 10.
        **kwargs: Additional arguments passed to pollForMessages function.
    """
    while True:
        pollForMessages(queueName, **kwargs)
        time.sleep(timeInMinutes * 60)


def loopForChunkingQueue(timeInMinutes: int = 0.1, **kwargs) -> None:
    """
    Continuously polls the Azure Chunking Queue at a specified interval.

    Args:
        timeInMinutes (int, optional): The interval between polls in minutes. Defaults to 10.
        **kwargs: Additional arguments passed to pollForMessages function.
    """
    loopForMessages(chunkingQueueName, timeInMinutes, **kwargs)
