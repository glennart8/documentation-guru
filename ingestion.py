import lancedb
import time
from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH
from backend.data_models import Documentation
from pypdf import pypdf as PdfReader
import docx



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

def extract_text_from_file(file_path):
    """Extraherar text baserat på filändelse."""
    suffix = file_path.suffix.lower()
    
    if suffix == ".pdf":
        if PdfReader is None:
            print(f"pypdf saknas. Hoppar över {file_path.name}")
            return ""
        try:
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            return "\n".join(text)
        except Exception as e:
            print(f"Fel vid läsning av PDF {file_path.name}: {e}")
            return ""

    elif suffix == ".docx":
        if docx is None:
            print(f"python-docx saknas. Hoppar över {file_path.name}")
            return ""
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Fel vid läsning av DOCX {file_path.name}: {e}")
            return ""
            
    else:
        # Standard textläsning för .md och .txt
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Fel vid läsning av fil {file_path.name}: {e}")
            return ""

def ingest_docs_to_vector_db(table):
    # Leta efter flera filtyper
    extensions = ["*.md", "*.txt", "*.pdf", "*.docx"]
    files = []
    for ext in extensions:
        files.extend(list(DATA_PATH.glob(ext)))
    
    for file in files:
        doc_id = file.stem
        
        # Kontrollera om filen redan finns i databasen
        existing = table.search().where(f"doc_id = '{doc_id}'").limit(1).to_list()
        if existing:
            print(f"Skipping {file.name} - already ingested.")
            continue

        content = extract_text_from_file(file)
        
        if not content:
            continue
            
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