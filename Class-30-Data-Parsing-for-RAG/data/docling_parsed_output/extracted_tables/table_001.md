| 0                     | 1                                                  | 2                                       |
|:----------------------|:---------------------------------------------------|:----------------------------------------|
| Section               | Parsing challenge                                  | Why it matters for RAG                  |
| Contracts             | Dense legal text, clause numbers, cross references | Need section-aware chunks and citations |
| Tables                | Merged headers, numeric columns, footnotes         | Need row/column preservation            |
| Images                | Architecture diagram, heatmap, scanned form        | Need OCR or multimodal extraction       |
| Multi-tenant metadata | client_id, document_id, contract_group_id          | Need access-safe retrieval              |