from .common_imports import *
def getChunks(text:str) -> list[str]:
  return text.split("\n")

def getChunksFromFiles(filepath: str, chunk_size=4000, chunk_overlap=20) :
  # if filepath.split(".")[-1] == "pdf":
  # works for muultiple formats
  
  #for pdf only
  chunks=get_pdf_chunks_from_url(filepath, chunk_size, chunk_overlap)
  return chunks
  

def get_pdf_chunks_from_url(path,chunk_size=4000,chunk_overlap=20):
    loader = OnlinePDFLoader(path)
    data = loader.load()
    #preprocess the data
    cleaned_text=clean_text(data[0].page_content)
    chunks=chunk_text(cleaned_text, chunk_size, chunk_overlap)
    return {
        'page_content':cleaned_text,
        
        'metadata':data[0].metadata,
        'chunks':[chunk.page_content for chunk in chunks]
            }

def clean_text(doc):
    nlp = spacy.load("en_core_web_sm")  # Loading spaCy NLP model
    doc = nlp(doc.lower())
    cleaned_text = " ".join([token.text for token in doc if not token.is_punct])
    return cleaned_text


def chunk_text(doc,chunk_size=4000,chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    length_function=len,
    is_separator_regex=False,
)
    chunks = text_splitter.create_documents([doc])
    return chunks

# chunks=getChunksFromFiles("https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/Resource-for-Organisation/AI/SGModelAIGovFramework2.pdf")
# cs=chunks['chunks']
# print(cs[0])
# print(type(cs))
# print(type(cs[0]))