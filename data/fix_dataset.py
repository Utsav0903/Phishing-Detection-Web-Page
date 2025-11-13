import pandas as pd
import os

# AUTO-DETECT CSV FILE
csv_files = [f for f in os.listdir(".") if f.endswith(".csv")]
if not csv_files:
    raise FileNotFoundError("No CSV file found in /data folder")
IN = csv_files[0]  # pick first detected CSV
print("✅ Detected CSV:", IN)

OUT = "urls_fixed.csv"

df = pd.read_csv(IN, encoding="latin1")

# clean column names
df.columns = [c.strip().lower() for c in df.columns]

# rename to required names
if "url" not in df.columns or "label" not in df.columns:
    raise ValueError("CSV must contain URL and Label columns")

def fix_label(val):
    v = str(val).lower().strip()
    return 1 if v in ["bad","phish","phishing","malicious","1"] else 0

df["label"] = df["label"].apply(fix_label)

def normalize_url(u):
    u = str(u).strip()
    if u.startswith("http"):
        return u
    return "http://" + u
df["url"] = df["url"].apply(normalize_url)

df.drop_duplicates(subset=["url"], inplace=True)

df.to_csv(OUT, index=False, encoding="utf-8")

print("✅ Saved:", OUT)
print("✅ Total rows:", len(df))
