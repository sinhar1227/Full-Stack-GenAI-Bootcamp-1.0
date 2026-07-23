# LangChain Document Loaders

LangChain provides different types of document loaders to load data from local files, websites, databases, cloud storage, productivity tools, audio/video sources, emails, and chats.

The main goal of these loaders is to convert different data sources into LangChain's common `Document` format:

```python
Document(
    page_content="actual extracted text",
    metadata={"source": "file name or data source"}
)
```

---

## 1. File-based Loaders

These loaders are used to load local files.

| Data Type | Example Loaders |
|---|---|
| Text | `TextLoader` |
| PDF | `PyPDFLoader`, `PyMuPDFLoader`, `PDFPlumberLoader`, `UnstructuredPDFLoader` |
| Word | `Docx2txtLoader`, `UnstructuredWordDocumentLoader` |
| CSV | `CSVLoader`, `UnstructuredCSVLoader` |
| Excel | `UnstructuredExcelLoader` |
| HTML | `UnstructuredHTMLLoader`, `BSHTMLLoader` |
| Markdown | `UnstructuredMarkdownLoader` |
| JSON | `JSONLoader` |
| YAML/TOML | `TomlLoader` |
| PowerPoint | `UnstructuredPowerPointLoader` |
| Subtitle | `SRTLoader` |
| Notebook | `NotebookLoader` |

---

## 2. Website / Web Loaders

These loaders are used to load web pages, sitemaps, URLs, and articles.

```text
WebBaseLoader
RecursiveUrlLoader
SitemapLoader
AsyncHtmlLoader
BSHTMLLoader
UnstructuredURLLoader
NewsURLLoader
```

### Use Case

```text
Website docs
↓
Load pages
↓
Chunk
↓
Embedding
↓
RAG
```

---

## 3. Database Loaders

These loaders are used to convert SQL/database rows into LangChain `Document` format.

```text
SQLDatabaseLoader
DuckDBLoader
SnowflakeLoader
CouchbaseLoader
TiDBLoader
SurrealDBLoader
```

In LangChain, database loaders can represent each row as a document.

---

## 4. Cloud Storage Loaders

These loaders are used to load files from cloud storage.

```text
S3DirectoryLoader
S3FileLoader
AzureBlobStorageContainerLoader
AzureBlobStorageFileLoader
GoogleCloudStorageDirectoryLoader
GoogleCloudStorageFileLoader
TencentCOSDirectoryLoader
TencentCOSFileLoader
DropboxLoader
SharePointLoader
```

### Use Case

```text
S3 bucket PDFs
↓
Loader
↓
Document objects
↓
RAG
```

---

## 5. Productivity / Workspace Loaders

These loaders are used to load data from company productivity and collaboration tools.

```text
NotionDirectoryLoader
ConfluenceLoader
SlackDirectoryLoader
GoogleDriveLoader
MicrosoftOneDriveLoader
GitHubIssuesLoader
GitLoader
TrelloLoader
AirtableLoader
```

### Use Case

```text
Company Notion + Slack + Google Drive
↓
Internal knowledge base
↓
RAG
```

---

## 6. Audio / Video Loaders

These loaders are used for audio/video transcript-based RAG.

```text
YoutubeLoader
GenericLoader + audio parser
AssemblyAILoader
TencentASRLoader
```

### Use Case

```text
YouTube video / meeting recording
↓
Transcript
↓
Chunks
↓
RAG
```

---

## 7. Email / Chat Loaders

These loaders are used to load emails and chat data.

```text
GMailLoader
OutlookMessageLoader
TelegramChatFileLoader
TelegramChatApiLoader
WhatsAppChatLoader
SlackDirectoryLoader
```

---

## Simple Classroom Explanation

LangChain document loaders are connectors. They connect different data sources like PDFs, websites, databases, S3, Google Drive, Notion, Slack, YouTube, emails, and chats into one common LangChain `Document(page_content, metadata)` format.

This common format makes it easy to use the same RAG pipeline:

```text
Load data
↓
Document(page_content, metadata)
↓
Chunking
↓
Embeddings
↓
Vector database
↓
Retriever
↓
LLM answer
```
