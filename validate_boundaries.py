# validate_boundaries.py
import pickle
import re
from pathlib import Path

BASE_DIR = BASE_DIR = Path(__file__).parent
CHUNKS_FILE = BASE_DIR / "data" / "processed" / "chunks.pkl"

with open(CHUNKS_FILE, "rb") as f:
    chunks = pickle.load(f)

boundary_issues = []

for idx, chunk in enumerate(chunks):
    content = chunk["content"].strip()

    # Skip very small chunks
    if len(content) < 300:
        continue

    first_line = content.splitlines()[0]
    last_char = content[-1]

    # Heuristics
    if first_line[:1].islower():
        boundary_issues.append((idx, "Starts with lowercase"))

    if re.match(r"^(and|or|but|however)\b", first_line.lower()):
        boundary_issues.append((idx, "Starts with conjunction"))

    if last_char not in ".;:":
        boundary_issues.append((idx, "Ends mid-sentence"))

print(f"Total chunks checked: {len(chunks)}")
print(f"Boundary issues found: {len(boundary_issues)}")

# Show a few problematic chunks
for issue in boundary_issues[:5]:
    i, reason = issue
    print("\n" + "-" * 70)
    print(f"Chunk #{i} | Issue: {reason}")
    print(chunks[i]["content"][:300])
