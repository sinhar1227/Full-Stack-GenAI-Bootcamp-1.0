#!/usr/bin/env python
# coding: utf-8

# Collections
# Unique record IDs
# Dense vectors
# Sparse vectors
# Multiple named vectors
# JSON payloads
# Metadata indexes
# Insert/update/upsert/delete
# Filtering
# Persistence
# Snapshots
# Replication and sharding
# HTTP/gRPC server

# Qdrant Database
# │
# ├── Collection: company-documents
# │     │
# │     ├── Point 1
# │     │     ├── ID
# │     │     ├── Dense vector
# │     │     └── Payload
# │     │
# │     ├── Point 2
# │     │     ├── ID
# │     │     ├── Dense vector
# │     │     └── Payload
# │     │
# │     └── Point 3
# │
# ├── Vector index
# │     └── HNSW / related retrieval indexes
# │
# ├── Payload index
# │     └── category, source, page, user_id...
# │
# └── Storage
#       ├── Memory
#       └── Disk

# In[1]:


from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from langchain_community.document_loaders import PyPDFLoader


# In[2]:


from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models


# In[13]:


COLLECTION_NAME = "company-policy-rag"


# In[16]:


# 1. Load PDF
loader = PyPDFLoader("D:\\complete_content_new\\Full-Stack-GenAI-Bootcamp-1.0\\Class-34-25-July-2026\\data\\llama2-research-paper.pdf")
pages = loader.load()

print("PDF pages loaded:", len(pages))


# In[18]:


# 2. Split documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=120,
)
chunks = text_splitter.split_documents(pages)
print("Chunks created:", len(chunks))


# In[19]:


# 3. Add useful metadata
for chunk_index, chunk in enumerate(chunks):
    chunk.metadata["chunk_id"] = chunk_index
    chunk.metadata["filename"] = "llama2-research-paper.pdf"


# In[21]:


# ---------------------------------------------------
# 2. Embedding model
# ---------------------------------------------------
from langchain_openai import OpenAIEmbeddings
embeddings=OpenAIEmbeddings(model="text-embedding-3-large")
dimension = len(
    embeddings.embed_query("dimension check")
)
print("Embedding dimension:", dimension)

dimension = len(
    embeddings.embed_query("dimension check")
)


# In[ ]:


# # 5. Local Qdrant
# client = QdrantClient(
#     path=str(Path(__file__).parent / "qdrant_data")
# )


# In[22]:


import os
from dotenv import load_dotenv
load_dotenv()
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_cluster_endpoint = os.getenv("QDRANT_Cluster_Endpoint")


# In[24]:


client = QdrantClient(api_key=qdrant_api_key, url=qdrant_cluster_endpoint)


# In[25]:


# 6. Create collection
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=dimension,
            distance=models.Distance.COSINE,
        ),
    )


# In[26]:


# 7. LangChain Qdrant vector store
vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)


# In[27]:


# 8. Use deterministic or stable IDs in production
chunk_ids = [
    str(uuid4())
    for _ in chunks
]


# In[28]:


# 9. Add documents
inserted_ids = vector_store.add_documents(
    documents=chunks,
    ids=chunk_ids,
)

print("Inserted chunks:", len(inserted_ids))


# In[29]:


query = "What is the annual leave policy?"

results = vector_store.similarity_search(
    query=query,
    k=4,
)

for rank, document in enumerate(results, start=1):
    print(f"\nResult {rank}")
    print("Content:", document.page_content)
    print("Metadata:", document.metadata)


# In[30]:


retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 4
    },
)

context_documents = retriever.invoke(
    "What benefits are available to employees?"
)

context = "\n\n".join(
    document.page_content
    for document in context_documents
)

print(context)


# In[ ]:




