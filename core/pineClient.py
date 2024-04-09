import os
from pinecone import Pinecone, PodSpec
    
class PineClient:
  instance = None
  def __init__(self) -> None:
    print("constructor")
    # self.client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    self.client = Pinecone(api_key="acfcd7d8-0ae5-4670-a505-18adc5dbf4a5")
  
  def getInstance():
    if PineClient.instance is None:
      PineClient.instance = PineClient()
    
    # return PineClient.instance.client
    return PineClient.instance
  
  def createIndex(self, index_name, dimension):
    raise NotImplementedError
    self.client.create_index(
      name=index_name,
      dimension=dimension,
      metric="cosine",
      spec=PodSpec(
        environment="gcp-starter",
        pod_type="starter"        
      )
    )
  
  def getIndex(self, index_name):
    return self.client.Index(index_name)
  
  def getValues(self, index_name, key_vector, cnt_results=10):
    index = self.getIndex(index_name=index_name)
    res = index.query(vector=key_vector, top_k=cnt_results, include_values=True, include_metadata=True)
    return [v["metadata"]["text"] for v in res["matches"]]
  
  def addValue(self, index_name, text:list[str], vectors:list[list[int]], doc_id:str):
    index = self.getIndex(index_name=index_name)
    records = []
    for idx in range(0, len(text)):
      records.append({
        "id": str(doc_id+idx),
        "values": vectors[idx],
        "metadata": {
          "text": text[idx],
          "doc_id": doc_id
        }
      })
    
    res = index.upsert(vectors=records)
    return res

if __name__ == "__main__":
  pc_client = PineClient.getInstance()
  # pc_client.createIndex("test", 4)
    

