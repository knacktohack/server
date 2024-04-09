from pineClient import PineClient

def getEmbedding(text: str) -> list[float]:
  return [0.1, 0.1, 0.1, 0.1]

def getContext(query: str) -> list[str]:
  query_vector = getEmbedding(query)
  pc_client = PineClient.getInstance()
  res = pc_client.getValues(index_name="test", key_vector=query_vector)
  return res

print(getContext("abc"))