from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os
from dotenv import load_dotenv
load_dotenv()

connectionString = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
containerName = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

def uploadToBlobStorage(filePath, fileName):
    try:
        blobServiceClient = BlobServiceClient.from_connection_string(connectionString)
        blobClient = blobServiceClient.get_blob_client(container=containerName, blob=fileName)
        with open(filePath, "rb") as data:
            res = blobClient.upload_blob(data)
            uploadUrl = blobClient.url
            print(res)
            print(uploadUrl)
            print(f"Uploaded {fileName}")
            
    except ResourceExistsError as e:
        print(f"ResourceExistsError: {e}")
