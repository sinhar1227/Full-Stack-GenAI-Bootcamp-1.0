| Layer               | Control                               | Failure mode if missing                     |
| ------------------- | ------------------------------------- | ------------------------------------------- |
| Authentication      | Identify user and organization        | Unknown user may access application         |
| Authorization       | Map user to client\_id and role       | User may retrieve another clients documents |
| Vector retrieval    | Filter by client\_id or namespace     | Retriever may return unauthorized chunks    |
| Prompt construction | Send only allowed context             | LLM may see sensitive data                  |
| Audit logging       | Record query, source chunks, user\_id | No traceability during incident review      |