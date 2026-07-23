| 0                 | 1                       | 2                                             |
|:------------------|:------------------------|:----------------------------------------------|
| Field             | Expected OCR value      | Validation rule                               |
| Client Name       | BlueLeaf Retail Pvt Ltd | Must match known client list                  |
| Contract ID       | BLR-MSA-2026-019        | Pattern: client-code + type + year + sequence |
| Effective Date    | 01 Apr 2026             | Date parser should normalize to ISO format    |
| Approval checkbox | Checked                 | Boolean extraction required                   |