#uv pip install nbconvert nbformat
#python convert_ipynb.py notebook.ipynb -o script.py

from pathlib import Path
import argparse
import nbformat
from nbconvert import PythonExporter


def convert_ipynb_to_py(notebook_path: str, output_path: str | None = None):
    notebook = Path(notebook_path)

    if not notebook.exists():
        raise FileNotFoundError(f"Notebook nahi mili: {notebook}")

    output = Path(output_path) if output_path else notebook.with_suffix(".py")

    with notebook.open("r", encoding="utf-8") as file:
        notebook_data = nbformat.read(file, as_version=4)

    exporter = PythonExporter()
    python_code, _ = exporter.from_notebook_node(notebook_data)

    output.write_text(python_code, encoding="utf-8")
    print(f"Converted successfully: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert IPYNB notebook to Python script")
    parser.add_argument("notebook", help="Input .ipynb file")
    parser.add_argument("-o", "--output", help="Output .py file (optional)")
    args = parser.parse_args()

    convert_ipynb_to_py(args.notebook, args.output)