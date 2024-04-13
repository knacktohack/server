from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os
import uuid
from dotenv import load_dotenv
load_dotenv()
from .message_queue import publishToChunkingQueue

connectionString = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
containerName = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

def uploadToBlobStorage(data,fileName,organizationId="knacktohack"):
    try:
        blobServiceClient = BlobServiceClient.from_connection_string(connectionString)
        containerClient = blobServiceClient.get_container_client(container=containerName)
        
        subFolderName = organizationId + "/"
        blobClient = containerClient.get_blob_client(blob = subFolderName)
        
        if not blobClient.exists():
            blobClient.upload_blob("")
            blobClient.delete_blob()
            print("Blob does not exist")
            
        fileName = subFolderName + fileName
        
        blobClient = blobServiceClient.get_blob_client(container = containerName,blob = fileName)
        
        uploadUrl = blobClient.url
    
        blobClient.upload_blob(data)
        publishToChunkingQueue({"url":uploadUrl,"file_name":fileName,"organization_id":organizationId})
            
    except ResourceExistsError as e:
        print(f"Blob {fileName} already exists")
        
    except Exception as e:
        print(e)
        raise e
    
    
def getAllFiles():
    try:
        blobServiceClient = BlobServiceClient.from_connection_string(connectionString)
        containerClient = blobServiceClient.get_container_client(containerName)
        blobs = containerClient.list_blobs()
        return [blob.name for blob in blobs]
    except Exception as e:
        print(e)
        raise e
    
    
def getAllFilesByOrganizationId(organizationId:str):
    try:
        #subfolder named organizationId
        blobServiceClient = BlobServiceClient.from_connection_string(connectionString)
        containerClient = blobServiceClient.get_container_client(containerName)
        
        subFolderName = organizationId + "/"
        
        blobs = containerClient.list_blobs(name_starts_with=subFolderName)
        
        '''
        return {"filename","url"}
        '''
        
        return [{"file_name":blob.name,"url":containerClient.url + "/" +blob.name} for blob in blobs]
    except Exception as e:
        print(e)
        raise e
        
