| Point | STDIO | HTTP / Streamable HTTP |
|---|---|---|
| **Best for** | Local MCP server | Remote / production MCP server |
| **Runs where?** | Usually same machine | Same machine ya different machine/cloud |
| **Connection kaise?** | Process input/output pipes | URL ke through |
| **Example** | `python server.py` launched by client | `https://api.company.com/mcp` |
| **Port needed?** | No | Yes |
| **URL needed?** | No | Yes |
| **Network needed?** | No | Usually yes |
| **Client server ko start karta hai?** | Usually yes | Usually no |
| **Server independently run karta hai?** | Usually no | Yes |
| **Authentication** | Usually not needed | OAuth / Bearer token common |
| **Production use** | Limited | Preferred |
| **SaaS/vendor MCP** | Rare | Mostly HTTP/HTTPS |
| **Scaling / load balancer** | Difficult | Easy |
| **Example use case** | VS Code local tool, local Python MCP | GitHub/Databricks/Notion remote MCP |