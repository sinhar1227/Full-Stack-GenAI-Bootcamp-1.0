| Asset ID      | Client            | Format      | Pages/Rows  | Expected extraction          | Notes                                    |
| ------------- | ----------------- | ----------- | ----------- | ---------------------------- | ---------------------------------------- |
| ARK-MSA-001   | Arka Finance      | PDF         | 32 pages    | Clauses, tables, signatures  | Born-digital text with footer references |
| ARK-DPA-002   | Arka Finance      | DOCX        | 18 pages    | Headings, lists, tables      | Track changes removed before ingestion   |
| BLR-PRICE-003 | BlueLeaf Retail   | XLSX        | 12 sheets   | Rate cards, discounts        | Merged cells and formulas                |
| BLR-SLA-004   | BlueLeaf Retail   | PDF         | 9 pages     | SLA table, escalation matrix | Table crosses page boundary              |
| CRM-OPS-005   | CityRide Mobility | CSV         | 48,200 rows | Incident records             | Needs column type normalization          |
| CRM-FORM-006  | CityRide Mobility | Scanned PDF | 4 pages     | OCR fields, checkbox         | Low contrast and slight rotation         |
| KB-RUN-007    | Shared            | Markdown    | 14 files    | Runbook sections             | Good for heading-based chunks            |
| WEB-FAQ-008   | Shared            | HTML        | 23 pages    | FAQ content, links           | Needs boilerplate removal                |