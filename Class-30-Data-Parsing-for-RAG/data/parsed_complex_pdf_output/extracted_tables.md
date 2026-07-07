

## Page 1 - Table 1

| Section               | Parsing challenge                       | Why it matters for RAG                  |
|:----------------------|:----------------------------------------|:----------------------------------------|
| Contracts             | Dense legal text, clause numbers, cross | Need section-aware chunks and citations |
|                       | references                              |                                         |
| Tables                | Merged headers, numeric columns,        | Need row/column preservation            |
|                       | footnotes                               |                                         |
| Images                | Architecture diagram, heatmap, scanned  | Need OCR or multimodal extraction       |
|                       | form                                    |                                         |
| Multi-tenant metadata | client_id, document_id,                 | Need access-safe retrieval              |
|                       | contract_group_id                       |                                         |

---


## Page 2 - Table 1

| Client            | Main document family        | Risk   | Primary users        | Typical question                    |
|:------------------|:----------------------------|:-------|:---------------------|:------------------------------------|
| Arka Finance      | MSA, audit addendum, DPA    | High   | Legal and compliance | What audit rights exist in the DPA? |
| BlueLeaf Retail   | MSA, pricing, support SLA   | Medium | Procurement          | Which clause controls renewal       |
|                   |                             |        |                      | pricing?                            |
| CityRide Mobility | Ops reports, incident logs, | Medium | Operations           | Which depot had repeated battery    |
|                   | SOPs                        |        |                      | incidents?                          |

---


## Page 3 - Table 1

| Asset ID     | Client            | Format      | Pages/Rows   | Expected extraction          | Notes                         |
|:-------------|:------------------|:------------|:-------------|:-----------------------------|:------------------------------|
| ARK-MSA-001  | Arka Finance      | PDF         | 32 pages     | Clauses, tables, signatures  | Born-digital text with footer |
|              |                   |             |              |                              | references                    |
| ARK-DPA-002  | Arka Finance      | DOCX        | 18 pages     | Headings, lists, tables      | Track changes removed         |
|              |                   |             |              |                              | before ingestion              |
| BLR-PRICE-00 | BlueLeaf Retail   | XLSX        | 12 sheets    | Rate cards, discounts        | Merged cells and formulas     |
| 3            |                   |             |              |                              |                               |
| BLR-SLA-004  | BlueLeaf Retail   | PDF         | 9 pages      | SLA table, escalation matrix | Table crosses page boundary   |
| CRM-OPS-005  | CityRide Mobility | CSV         | 48,200 rows  | Incident records             | Needs column type             |
|              |                   |             |              |                              | normalization                 |
| CRM-FORM-00  | CityRide Mobility | Scanned PDF | 4 pages      | OCR fields, checkbox         | Low contrast and slight       |
| 6            |                   |             |              |                              | rotation                      |
| KB-RUN-007   | Shared            | Markdown    | 14 files     | Runbook sections             | Good for heading-based        |
|              |                   |             |              |                              | chunks                        |
| WEB-FAQ-008  | Shared            | HTML        | 23 pages     | FAQ content, links           | Needs boilerplate removal     |

---


## Page 4 - Table 1

|   Clause | Short name      | Owner            | Trigger                 | Required action                          | Citation hint   |
|---------:|:----------------|:-----------------|:------------------------|:-----------------------------------------|:----------------|
|      7.2 | Confidentiality | Receiving Party  | Receipt of confidential | Protect information with reasonable care | Page 4, clause  |
|          |                 |                  | material                | and equivalent internal controls         | 7.2             |
|      9.1 | Data residency  | Service Provider | SOW specifies region    | Process production records only in       | Page 4, clause  |
|          |                 |                  |                         | approved region                          | 9.1             |
|     11.4 | Termination     | Service Provider | Agreement               | Provide export window for 30 days        | Page 4, clause  |
|          | assistance      |                  | termination             |                                          | 11.4            |

---


## Page 5 - Table 1

| Policy Area       | Rule                                                 | Owner            | Review Cycle        |
|:------------------|:-----------------------------------------------------|:-----------------|:--------------------|
| Refunds           | Refund requests must be raised within 7 days of      | Customer Support | Quarterly           |
|                   | purchase.                                            |                  |                     |
| Data Export       | Client admins can request export in CSV or JSON      | Platform Ops     | Monthly             |
|                   | format.                                              |                  |                     |
| Access Review     | Privileged access must be reviewed every 30 days.    | Security         | Monthly             |
| Incident Response | Critical incidents require acknowledgement within 30 | SRE              | After each incident |
|                   | minutes.                                             |                  |                     |
| Vendor Review     | High-risk vendors require annual risk assessment.    | Procurement      | Annual              |

---


## Page 6 - Table 1

| Service Category   | Severity       | Response Target   | Resolution Target   | Service Credit         | Evidence Required              |
|:-------------------|:---------------|:------------------|:--------------------|:-----------------------|:-------------------------------|
| API Availability   | P1 - complete  | 15 minutes        | 4 hours             | 10 percent monthly     | Monitoring logs and incident   |
|                    | outage         |                   |                     | fee credit             | ticket                         |
| API Availability   | P2 - degraded  | 30 minutes        | 8 hours             | 5 percent monthly fee  | Latency dashboard and          |
|                    | performance    |                   |                     | credit                 | affected endpoint list         |
| Data Pipeline      | P1 - ingestion | 20 minutes        | 6 hours             | 8 percent pipeline fee | Queue depth, failed job IDs,   |
|                    | stopped        |                   |                     | credit                 | replay report                  |
| Data Pipeline      | P3 - delayed   | 4 hours           | Next business day   | No automatic credit    | Batch ID and SLA exception     |
|                    | batch          |                   |                     |                        | note                           |
| Support            | P2 - urgent    | 1 hour            | 1 business day      | 2 percent support fee  | Support ticket with timestamps |
|                    | support        |                   |                     | credit                 |                                |

---


## Page 7 - Table 1

| Image element   | Potential extraction method    | Expected output                      |
|:----------------|:-------------------------------|:-------------------------------------|
| Box labels      | OCR or vision model            | Raw Files, Parser, Chunks, Vector DB |
| Arrows          | Layout or vision understanding | Processing order                     |
| Caption         | Normal PDF text extraction     | Description of the diagram           |

---


## Page 8 - Table 1

| Runbook field   | Value                      | Parsing expectation                     |
|:----------------|:---------------------------|:----------------------------------------|
| Title           | Contract Ingestion Failure | Should become section title metadata    |
| Symptoms        | Five bullet items          | Should remain as list or separate lines |
| Recovery Steps  | Numbered sequence          | Order must be preserved                 |

---


## Page 9 - Table 1

| Field             | Expected OCR value      | Validation rule                      |
|:------------------|:------------------------|:-------------------------------------|
| Client Name       | BlueLeaf Retail Pvt Ltd | Must match known client list         |
| Contract ID       | BLR-MSA-2026-019        | Pattern: client-code + type + year + |
|                   |                         | sequence                             |
| Effective Date    | 01 Apr 2026             | Date parser should normalize to ISO  |
|                   |                         | format                               |
| Approval checkbox | Checked                 | Boolean extraction required          |

---


## Page 10 - Table 1

| document_id   | document_type     | contract_group_id   | effective_date   | relationship                       |
|:--------------|:------------------|:--------------------|:-----------------|:-----------------------------------|
| BLR-MSA-001   | Master Service    | BLR-ACME-2026       | 2026-04-01       | Base commercial agreement          |
|               | Agreement         |                     |                  |                                    |
| BLR-NDA-002   | NDA               | BLR-ACME-2026       | 2026-04-01       | Confidentiality terms              |
| BLR-SOW-003   | Statement of Work | BLR-ACME-2026       | 2026-04-15       | Project scope and deliverables     |
| BLR-PRICE-004 | Pricing Amendment | BLR-ACME-2026       | 2026-05-01       | Updated pricing and discount tiers |
| BLR-SLA-005   | Support SLA       | BLR-ACME-2026       | 2026-05-10       | Support response and credits       |

---


## Page 11 - Table 1

| Layer               | Control                              | Failure mode if missing                     |
|:--------------------|:-------------------------------------|:--------------------------------------------|
| Authentication      | Identify user and organization       | Unknown user may access application         |
| Authorization       | Map user to client_id and role       | User may retrieve another clients documents |
| Vector retrieval    | Filter by client_id or namespace     | Retriever may return unauthorized chunks    |
| Prompt construction | Send only allowed context            | LLM may see sensitive data                  |
| Audit logging       | Record query, source chunks, user_id | No traceability during incident review      |

---


## Page 12 - Table 1

| Observation                | Supporting value        | Scheduling implication                           |
|:---------------------------|:------------------------|:-------------------------------------------------|
| Prime Friday performs best | 93 retention score      | Place premium content in Friday late/prime slots |
| Early week late slots      | 10 to 21 score range    | Avoid launching new series in weak slots         |
| underperform               |                         |                                                  |
| Evening improves midweek   | 77 on Wednesday evening | Use midweek evening for discovery content        |

---


## Page 13 - Table 1

| Test ID   | Question                        | Expected source    | Expected answer element    | Failure signal      |
|:----------|:--------------------------------|:-------------------|:---------------------------|:--------------------|
| Q-001     | What is the refund window?      | Policy Rules table | 7 days                     | Answer says 30 days |
| Q-002     | Which clause covers data        | Clause 9.1         | Approved processing region | No clause citation  |
|           | residency?                      |                    |                            |                     |
| Q-003     | What is P1 API response target? | SLA table          | 15 minutes                 | Wrong severity row  |
| Q-004     | Which documents belong to       | Relationship table | Five related documents     | Only one document   |
|           | BLR-ACME-2026?                  |                    |                            | returned            |
| Q-005     | Who owns access review?         | Policy Rules table | Security                   | Owner missing       |

---


## Page 14 - Table 1

| Edge case              | Example                             | Recommended handling                         |
|:-----------------------|:------------------------------------|:---------------------------------------------|
| Repeated headers and   | Page number, confidentiality banner | Remove or store separately as metadata       |
| footers                |                                     |                                              |
| Hyphenated line breaks | termi- nation assistance            | Normalize during cleaning                    |
| Rotated tables         | Landscape appendix in PDF           | Use layout-aware parser or OCR               |
| Merged cells           | Pricing table with grouped plans    | Preserve hierarchy in row text               |
| Scanned signatures     | Signature block as image            | OCR if text is needed; store image reference |
| Boilerplate navigation | Website header and footer           | Use boilerplate removal                      |
| Duplicate chunks       | Same policy in FAQ and PDF          | Deduplicate using source and hash            |

---


## Page 15 - Table 1

| Checklist item   | Status to verify                              | Why it matters                       |
|:-----------------|:----------------------------------------------|:-------------------------------------|
| Text extraction  | Paragraphs are readable and ordered           | Prevents noisy chunks                |
| Table extraction | Rows, columns, headers, and footnotes         | Protects factual answers             |
|                  | preserved                                     |                                      |
| Image handling   | Captions indexed and OCR done if required     | Avoids missing visual information    |
| Metadata         | source, page, client_id, document_id          | Enables citations and access control |
|                  | captured                                      |                                      |
| Chunking         | Chunks preserve meaning and section           | Improves retrieval relevance         |
|                  | boundaries                                    |                                      |
| Access control   | Retrieval filters use authenticated client_id | Prevents data leakage                |
| Evaluation       | Golden questions tested with citations        | Measures real answer quality         |

---


## Page 24 - Table 1

| Element        | Parsing Challenge                         | Expected Handling                                    |
|:---------------|:------------------------------------------|:-----------------------------------------------------|
| Portrait image | Pixels are not selectable PDF text.       | Extract image object or create visual summary with a |
|                |                                           | multimodal model.                                    |
| Caption text   | Caption should stay attached to image     | Preserve caption near the image in reading order.    |
|                | context.                                  |                                                      |
| Image metadata | File name, page, and bounding box may be  | Store metadata for citation and retrieval.           |
|                | needed.                                   |                                                      |
| RAG usage      | Text-only chunks may miss visual details. | Use OCR or vision captioning before chunking if      |
|                |                                           | visual content matters.                              |

---
