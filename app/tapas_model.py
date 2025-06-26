import re
import pandas as pd
from transformers import TapasTokenizer, TapasForQuestionAnswering
from app.config import TAPAS_MODEL
from io import StringIO

# Load TAPAS model
tapas_tokenizer = TapasTokenizer.from_pretrained(TAPAS_MODEL)
tapas_model = TapasForQuestionAnswering.from_pretrained(TAPAS_MODEL)

# === Heuristic: Table Query Detection ===
def is_table_query(question):
    keywords = [
        "rate", "growth", "%", "total", "sum", "average", "mean", "min", "max", "minimum", "maximum", "revenue", "profit", "cost",
        "change", "difference", "increase", "decrease", "Name of the Company", "Company Name", "Company",
        "Age", "Salary", "EstimatedSalary", "Nature of transactions", "Outstanding", "No. of Shares as on March 31, 2024",
        "Transactions during the year March 31, 2024", "Balance Outstanding as on March 31, 2024",
        "Balance Outstanding as on March 31, 2023", "Balance Outstanding as on", "Nature of transactions with struck off Company",
        "Balance Outstanding as on March 31, 2022", "Balance Outstanding as on March 31, 2021",
        "Relationship with the Struck off Company"
    ]
    return any(k.lower() in question.lower() for k in keywords)

# === Table title matcher (fallback: first table) ===
def select_table_by_title(tables, question):
    q_norm = re.sub(r"[^a-z0-9]", "", question.lower())
    for t in tables:
        t_norm = re.sub(r"[^a-z0-9]", "", t["title"].lower())
        if t_norm in q_norm:
            return t
    return tables[0]

# === Table content matcher (fuzzy match) ===
def select_table_by_content(tables, question):
    matches = [t for t in tables if any(word in t['table'].lower() for word in question.lower().split())]
    return matches[0] if matches else tables[0]

# === Markdown to DataFrame ===
def markdown_to_dataframe(markdown_table):
    cleaned = "\n".join(
        line for i, line in enumerate(markdown_table.strip().splitlines())
        if i != 1 and line.strip().startswith("|")
    )
    try:
        df = pd.read_csv(StringIO(cleaned), sep="|", engine="python")
        df = df.dropna(axis=1, how="all")
        df.columns = df.columns.astype(str)
        return df
    except Exception as e:
        print(f"[TAPAS] Error parsing markdown:\n{e}")
        return pd.DataFrame()

# === Clean & prepare table ===
def preprocess_table(df):
    df = df.fillna("")
    df = df.astype(str)
    return df

# === Main TAPAS Answer Function with aggregations ===
def tapas_answer(df, question):
    if df.empty:
        return "No valid table found."

    df = preprocess_table(df)

    inputs = tapas_tokenizer(table=df, queries=[question], return_tensors="pt")
    outputs = tapas_model(**inputs)

    answers, _ = tapas_tokenizer.convert_logits_to_predictions(
        inputs,
        outputs.logits.detach(),
        outputs.logits_aggregation.detach()
    )

    selected_cells = answers[0]
    extracted = []
    for row, col in selected_cells:
        if row < df.shape[0] and col < df.shape[1]:
            extracted.append(df.iat[row, col])
        else:
            print(f"[⚠️ TAPAS] Ignored out-of-bounds cell: ({row}, {col})")

    if not extracted:
        return "No relevant answer found."

    # === Try numeric extraction ===
    def to_float(x):
        try:
            return float(str(x).replace(",", "").replace("₹", "").replace("%", "").strip())
        except:
            return None

    numeric_vals = list(filter(None, [to_float(x) for x in extracted]))
    q_lower = question.lower()

    if "sum" in q_lower or "total" in q_lower:
        if numeric_vals:
            return f"Sum: {sum(numeric_vals):,.2f}"
    elif "average" in q_lower or "mean" in q_lower:
        if numeric_vals:
            return f"Average: {sum(numeric_vals)/len(numeric_vals):,.2f}"
    elif "min" in q_lower or "minimum" in q_lower:
        if numeric_vals:
            return f"Minimum: {min(numeric_vals):,.2f}"
    elif "max" in q_lower or "maximum" in q_lower:
        if numeric_vals:
            return f"Maximum: {max(numeric_vals):,.2f}"
    elif "%" in q_lower or "percent" in q_lower or "percentage" in q_lower:
        if numeric_vals:
            return f"Percentage(s): {', '.join(f'{v:.2f}%' for v in numeric_vals)}"

    return ", ".join(extracted)
