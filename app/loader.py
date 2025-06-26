# from pathlib import Path

# def load_text_chunks(path="data/text_chunks.md"):
#     with open(path, "r", encoding="utf-8") as f:
#         lines = f.read().split("\n## ")
#         return [{"text": line.strip()} for line in lines if line.strip()]

# def load_markdown_tables(path="data/tables.md"):
#     tables = []
#     with open(path, "r", encoding="utf-8") as f:
#         raw = f.read()
#     blocks = raw.strip().split("\n### ")
#     for block in blocks:
#         if not block.strip():
#             continue
#         parts = block.split("\n", 1)
#         title = parts[0].strip()
#         markdown_table = parts[1].strip()
#         tables.append({"title": title, "markdown": markdown_table})
#     return tables


#-------------------------------------------------------------------------------------------------

import re

def load_text_chunks(path, chunk_size=500, overlap=100):
    with open(path, "r", encoding="utf-8") as f:
        full_text = f.read()
    chunks = []
    start = 0
    while start < len(full_text):
        end = min(len(full_text), start + chunk_size)
        chunk = full_text[start:end]
        chunks.append({"text": chunk})
        start += chunk_size - overlap
    return chunks

def load_tables(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    tables = []
    parts = content.split("### ")
    for part in parts[1:]:
        lines = part.strip().splitlines()
        title = lines[0].strip()
        table_md = "\n".join(lines[1:])
        tables.append({"title": title, "table": table_md})
    return tables
