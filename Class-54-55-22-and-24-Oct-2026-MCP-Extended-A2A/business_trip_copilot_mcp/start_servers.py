import subprocess
import sys

servers = [
    ("Travel MCP", "http_servers/travel_http_server.py", 8001),
    ("Policy MCP", "http_servers/policy_http_server.py", 8002),
    ("Work MCP", "http_servers/work_http_server.py", 8003),
]

processes = []

for name, server_file, port in servers:
    process = subprocess.Popen(
        [sys.executable, server_file]
    )

    processes.append(process)

    print(
        f"{name} started at "
        f"http://127.0.0.1:{port}/mcp"
    )

print("\nAll MCP servers are running.")

for process in processes:
    process.wait()