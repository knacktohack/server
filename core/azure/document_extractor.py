from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import requests as Requests
import os

endpoint = os.getenv("AZURE_DOCUMENT_ENDPOINT")
accessKey = os.getenv("AZURE_DOCUMENT_ACCESS_KEY")


def extractFullPageText(pdfUrl):
  """
  Extracts full page text from a PDF at the specified URL using Azure Document Intelligence.

  Args:
      pdfUrl (str): The URL of the PDF document.
      endpoint (str): The endpoint URL of your Azure Document Intelligence resource.
      accessKey (str): The access key for your Azure Document Intelligence resource.

  Returns:
      str: The extracted full page text from the PDF.
  """

  # Create the DocumentAnalysisClient with credentials
  credential = AzureKeyCredential(accessKey)
  client = DocumentAnalysisClient(endpoint=endpoint, credential=credential)

  try:
    # Download the PDF content from the URL
    response = Requests.get(pdfUrl)
    response.raise_for_status()  # Raise exception for download errors
    document = response.content
    # with open("test.txt", "wb") as f:
    #   f.write(document)
    # print(document)
    # Analyze the PDF and extract text
    fullPageText = ""
    poller = client.begin_analyze_document("prebuilt-layout",document=document)  # Replace "invoice" with your model if needed
    result = poller.result()


    for page in result.pages:
        for line in page.lines:
            fullPageText += line.content + "\n"

    return fullPageText

  except Requests.exceptions.RequestException as e:
    print(f"Error Downloading PDF: {e}")
    return None  # Indicate error