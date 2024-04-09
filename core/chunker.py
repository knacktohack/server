from PyPDF2 import PdfReader

def getChunks(text:str) -> list[str]:
  return text.split("\n")

def getChunksFromFiles(filepath: str) -> str:
  # if filepath.split(".")[-1] == "pdf":
  # works for muultiple formats
  reader = PdfReader(filepath)
  text = ""
  for page in reader.pages:
    text += page.extract_text() + "\n"
  
  return getChunks(text)
  


