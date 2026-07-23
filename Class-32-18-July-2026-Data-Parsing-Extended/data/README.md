# LangChain Document Loader Sample Files

These files are made for testing these LangChain loaders:

```python
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
    JSONLoader,
)
```

## Files

- `sample_text.txt` -> TextLoader
- `sample_document.pdf` -> PyPDFLoader
- `sample_data.csv` -> CSVLoader
- `sample_document.docx` -> Docx2txtLoader
- `sample_page.html` -> UnstructuredHTMLLoader
- `sample_data.json` -> JSONLoader

## Basic usage

```python
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader, Docx2txtLoader, UnstructuredHTMLLoader, JSONLoader

text_docs = TextLoader('sample_text.txt').load()
pdf_docs = PyPDFLoader('sample_document.pdf').load()
csv_docs = CSVLoader('sample_data.csv').load()
docx_docs = Docx2txtLoader('sample_document.docx').load()
html_docs = UnstructuredHTMLLoader('sample_page.html').load()
json_docs = JSONLoader(file_path='sample_data.json', jq_schema='.[].content', text_content=True).load()
```
