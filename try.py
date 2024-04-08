# from PyPDF2 import PdfReader

# reader = PdfReader("out/demo.pdf")

# text = ""
# for page in reader.pages:
#   text += page.extract_text() + "\n"

# print(text)

from pinecone import Pinecone

pc = Pinecone(api_key="")
index = pc.Index("test")

# print(pc.describe_index("test"))

# res = index.upsert(vectors=[
#   {
#     "id": "1",
#     "values": [0.1, 0.2, 0.3, 0.1],
#     "metadata": {
#       "text": "interesting text",
#       "doc_id": 2
#     }
#   }, 
#   {
#     "id": "2",
#     "values": [0.1, 0.1, 0.1, 0.2],
#     "metadata": {
#       "text": "random text",
#       "doc_id": 1
#     }
#   }, 
#   {
#     "id": "3",
#     "values": [0.6, 0.2, 0.3, 0.6],
#     "metadata": {
#       "text": "some text",
#       "doc_id": 1
#     }
#   }, 
#   ])

# print(res)

res = index.query(
    vector=[0.1, 0.1, 0.1, 0.1],
    top_k=4,
    include_values=True,
    include_metadata=True,
    filter={"doc_id": {"$eq": 1}}
)

print(res)
print([v["metadata"]["text"] for v in res["matches"]])