import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

from docling.document_converter import DocumentConverter
from pathlib import Path

output_text_path = Path("data/text_chunks.md")
output_table_path = Path("data/tables.md")

def extract_pdf_to_markdown(pdf_path):
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document

    # Save full markdown text
    output_text_path.parent.mkdir(parents=True, exist_ok=True)
    with output_text_path.open("w", encoding="utf-8") as f_text:
        f_text.write(doc.export_to_markdown())

    # Save each table
    output_table_path.parent.mkdir(parents=True, exist_ok=True)
    with output_table_path.open("w", encoding="utf-8") as f_table:
        for i, table in enumerate(doc.tables, start=1):
            f_table.write(f"### Table {i}\n")
            f_table.write(table.export_to_markdown() + "\n\n")


    print("✅ Extraction complete.")

if __name__ == "__main__":
    extract_pdf_to_markdown("stem lem models.pdf")

#---------------------------------------------------------------------------------------------------------------------------------

# import nltk
# nltk.download("punkt")

# import os
# os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

# from docling.document_converter import DocumentConverter
# from pathlib import Path
# from nltk.tokenize import sent_tokenize

# output_text_path = Path("data/text_chunks.md")
# output_table_path = Path("data/tables.md")
# text_chunk_jsonl_path = Path("text_chunks.jsonl")

# CHUNK_SENTENCE_TOKEN_LIMIT = 100


# def sentence_chunker(text, max_tokens=CHUNK_SENTENCE_TOKEN_LIMIT):
#     sentences = sent_tokenize(text)
#     chunks = []
#     chunk = []
#     token_count = 0

#     for sent in sentences:
#         tokens = sent.split()  # basic token approximation
#         if token_count + len(tokens) > max_tokens:
#             chunks.append(" ".join(chunk))
#             chunk = []
#             token_count = 0
#         chunk.append(sent)
#         token_count += len(tokens)

#     if chunk:
#         chunks.append(" ".join(chunk))

#     return chunks


# def extract_pdf_to_markdown(pdf_path):
#     converter = DocumentConverter()
#     result = converter.convert(pdf_path)
#     doc = result.document

#     # Save full markdown text
#     output_text_path.parent.mkdir(parents=True, exist_ok=True)
#     with output_text_path.open("w", encoding="utf-8") as f_text:
#         f_text.write(doc.export_to_markdown())

#     # Save text chunks (sentence-wise) for RAG in .jsonl format
#     with text_chunk_jsonl_path.open("w", encoding="utf-8") as f_jsonl:
#         for block in doc.blocks:
#             chunks = sentence_chunker(block.text)
#             for chunk in chunks:
#                 f_jsonl.write(f"{{\"text\": {chunk!r}}}\n")

#     # Save each table
#     output_table_path.parent.mkdir(parents=True, exist_ok=True)
#     with output_table_path.open("w", encoding="utf-8") as f_table:
#         for i, table in enumerate(doc.tables, start=1):
#             f_table.write(f"### Table {i}\n")
#             f_table.write(table.export_to_markdown() + "\n\n")

#     print("✅ Extraction complete.")


# if __name__ == "__main__":
#     extract_pdf_to_markdown("MMManual_50.pdf")
