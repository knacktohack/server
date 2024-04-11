from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os
import uuid
from dotenv import load_dotenv
load_dotenv()
from .message_queue import publishToChunkingQueue

connectionString = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
containerName = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

def uploadToBlobStorage(data,fileName):
    try:
        blobServiceClient = BlobServiceClient.from_connection_string(connectionString)
        blobClient = blobServiceClient.get_blob_client(container=containerName, blob=fileName)
            
        uploadUrl = blobClient.url
    
        blobClient.upload_blob(data)
        publishToChunkingQueue({"url":uploadUrl,"fileName":fileName})
            
    except ResourceExistsError as e:
        #generate random filename
        fileName = str(uuid.uuid4()) + fileName
        
        uploadToBlobStorage(data,fileName)
        
    except Exception as e:
        print(e)
        raise e
        
