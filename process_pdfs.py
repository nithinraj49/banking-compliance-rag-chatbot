# process_pdfs_fast.py
import re
import pickle
from pathlib import Path
import sys

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 1500  # Characters per chunk
OVERLAP = 200      # Overlap between chunks

# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def detect_regulator(filename: str):
    f = filename.lower()
    if "rbi" in f:
        return "Reserve Bank of India", "India"
    if "fatf" in f:
        return "FATF", "International"
    if "basel" in f:
        return "Basel Committee", "International"
    if "uae" in f or "cbuae" in f:
        return "UAE Central Bank", "UAE"
    return "Unknown", "Unknown"


def extract_text_fast(pdf_path: Path):
    """Fast text extraction"""
    print(f"   → Reading PDF...", end="", flush=True)
    
    try:
        reader = PdfReader(pdf_path, strict=False)
        total_pages = len(reader.pages)
        print(f" {total_pages} pages")
        
        full_text = ""
        for i, page in enumerate(reader.pages):
            if i % 25 == 0 and i > 0:
                print(f"      Progress: {i}/{total_pages} pages", flush=True)
            
            text = page.extract_text()
            if text:
                full_text += text + "\n\n"
        
        print(f"   → ✅ Extracted {len(full_text):,} characters")
        return full_text
        
    except Exception as e:
        print(f"\n   ❌ ERROR: {e}")
        return ""


def simple_chunk(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Simple sliding window chunking"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if len(chunk.strip()) > 100:  # Only add non-empty chunks
            chunks.append(chunk.strip())
        
        start += (chunk_size - overlap)
    
    return chunks


# ============================================================
# MAIN PIPELINE
# ============================================================
print("=" * 70)
print("📄 FAST PDF PROCESSING")
print("=" * 70)

print(f"\n📁 Looking for PDFs in: {DATA_DIR}")
pdf_files = list(DATA_DIR.glob("*.pdf"))

if not pdf_files:
    print(f"\n❌ No PDF files found")
    sys.exit(1)

print(f"\n✅ Found {len(pdf_files)} PDFs:")
for i, pdf in enumerate(pdf_files, 1):
    size_mb = pdf.stat().st_size / (1024 * 1024)
    print(f"   {i}. {pdf.name} ({size_mb:.2f} MB)")

print("\n" + "=" * 70)
print("PROCESSING")
print("=" * 70)

all_chunks = []

for file_num, pdf_path in enumerate(pdf_files, 1):
    print(f"\n[{file_num}/{len(pdf_files)}] 📘 {pdf_path.name}")
    
    try:
        regulator, jurisdiction = detect_regulator(pdf_path.name)
        print(f"   → Regulator: {regulator}")
        
        # Extract text
        full_text = extract_text_fast(pdf_path)

        if not full_text or len(full_text) < 100:
            print("   ⚠️ SKIPPED: No text extracted")
            continue

        # Create chunks
        print(f"   → Chunking...", flush=True)
        text_chunks = simple_chunk(full_text)
        
        # Add metadata
        for i, chunk_text in enumerate(text_chunks, 1):
            all_chunks.append({
                "content": chunk_text,
                "source": pdf_path.name,
                "regulator": regulator,
                "jurisdiction": jurisdiction,
                "chunk_number": i,
                "total_chunks": len(text_chunks)
            })

        print(f"   → ✅ Created {len(text_chunks)} chunks")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        continue

# ============================================================
# SAVE OUTPUT
# ============================================================
print("\n" + "=" * 70)
print("💾 SAVING")
print("=" * 70)

chunks_file = PROCESSED_DIR / "chunks.pkl"
with open(chunks_file, "wb") as f:
    pickle.dump(all_chunks, f)

summary_file = PROCESSED_DIR / "summary.txt"
with open(summary_file, "w", encoding="utf-8") as f:
    f.write(f"Total PDFs: {len(pdf_files)}\n")
    f.write(f"Total chunks: {len(all_chunks)}\n\n")
    
    f.write("Chunks by Source:\n")
    sources = {}
    for c in all_chunks:
        sources[c["source"]] = sources.get(c["source"], 0) + 1
    
    for source, count in sorted(sources.items()):
        f.write(f"{source}: {count} chunks\n")
    
    f.write("\nChunks by Regulator:\n")
    regulators = {}
    for c in all_chunks:
        regulators[c["regulator"]] = regulators.get(c["regulator"], 0) + 1
    
    for r, count in sorted(regulators.items()):
        f.write(f"{r}: {count} chunks\n")

print(f"\n✅ Saved to: {chunks_file}")
print(f"✅ Summary: {summary_file}")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print(f"📦 Total chunks: {len(all_chunks)}")
print(f"📊 Average per PDF: {len(all_chunks)//len(pdf_files)}")
print("\n🚀 READY FOR PHASE 2")
print("=" * 70)