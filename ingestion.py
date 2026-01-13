import lancedb
import time
from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH
from backend.data_models import Documentation

def setup_vector_db(path):
    vector_db = lancedb.connect(uri = path)
    vector_db.create_table(name = "documentation", schema=Documentation, exist_ok=True)
    
    return vector_db

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Simple sliding window chunker.
    Splits text into chunks of size `chunk_size` with `overlap`.
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        # Move forward by chunk_size - overlap
        start += chunk_size - overlap
        
    return chunks

def ingest_docs_to_vector_db(table):
    # Look for both .md and .txt files
    files = list(DATA_PATH.glob("*.md")) + list(DATA_PATH.glob("*.txt"))
    
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            
        doc_id = file.stem
        # Remove existing entries for this file to avoid duplicates
        table.delete(f"doc_id = '{doc_id}'")

        chunks = chunk_text(content)
        data_to_add = []
        
        for i, chunk in enumerate(chunks):
            data_to_add.append({
                "doc_id": doc_id,
                "filepath": str(file),
                "filename": f"{file.stem} (part {i+1})",
                "content": chunk
            })
        
        if data_to_add:
            # Batch ingestion to avoid rate limits (Gemini free tier is ~100 req/min)
            batch_size = 5
            for i in range(0, len(data_to_add), batch_size):
                batch = data_to_add[i:i + batch_size]
                table.add(batch)
                print(f"Ingested batch {i // batch_size + 1} ({(i + len(batch))} / {len(data_to_add)} chunks) from {file.name}")
                time.sleep(4)

if __name__ == "__main__":
    vector_db = setup_vector_db(VECTOR_DATABASE_PATH)
    ingest_docs_to_vector_db(vector_db["documentation"])