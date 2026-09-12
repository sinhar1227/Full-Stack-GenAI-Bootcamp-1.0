# Memory-Augmented RAG — Modular Demo

This project demonstrates four different information sources:

1. **Short-term memory** — recent messages for one session.
2. **Long-term memory** — persistent user facts stored in SQLite.
3. **Semantic memory** — relevant previous interactions retrieved by similarity.
4. **RAG knowledge base** — business/domain documents retrieved by similarity.

## Architecture

```text
Current Query
    |
    +--> Short-Term Memory
    +--> Long-Term Memory
    +--> Semantic Memory
    +--> RAG Knowledge Base
              |
              v
         Context Fusion
              |
              v
             LLM
              |
              v
            Answer
              |
              +--> Update short-term memory
              +--> Update semantic memory
              +--> Save explicit long-term memory when user writes:
                   Remember: ...
```

## 1. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Set your OpenAI API key

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="your-key"
```

### macOS/Linux

```bash
export OPENAI_API_KEY="your-key"
```

Optional:

```bash
export OPENAI_MODEL="gpt-4.1-mini"
```

## 4. Run the app

```bash
python main.py
```

Try:

```text
Remember: I prefer concise answers.
How long is the probation period?
How many paid leaves do employees receive?
```

## 5. Run the offline self-test

The self-test does not require OpenAI or sentence-transformers.

```bash
python self_test.py
```

Expected:

```text
ALL OFFLINE TESTS PASSED
```

## Notes

- The local vector search uses NumPy cosine similarity to keep the teaching code simple.
- The real embedding model is `sentence-transformers/all-MiniLM-L6-v2`.
- Long-term memory is persistent because it is stored in SQLite.
- Short-term and semantic memory are in-process demo stores.
- In production, replace these demo stores with Redis/Postgres/pgvector/Qdrant/Pinecone/etc.

| Component                        | Kya store hota hai                          | DB options                                                                         |
| -------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Short-term memory**            | Recent chat/session messages                | **Redis**, PostgreSQL, DynamoDB, MongoDB                                           |
| **Long-term memory**             | User facts, preferences, profile, decisions | **PostgreSQL**, MongoDB, DynamoDB, MySQL, SQLite                                   |
| **Semantic memory**              | Previous interactions + embeddings          | **pgvector**, Qdrant, Pinecone, Weaviate, Milvus, Chroma, OpenSearch               |
| **RAG knowledge base**           | Document chunks + embeddings                | **pgvector**, Qdrant, Pinecone, Weaviate, Milvus, OpenSearch, Elasticsearch, FAISS |
| **Conversation history / audit** | Full chat logs                              | PostgreSQL, MongoDB, DynamoDB, S3                                                  |
| **Metadata**                     | document_id, user_id, source, timestamps    | PostgreSQL, MongoDB, DynamoDB                                                      |
