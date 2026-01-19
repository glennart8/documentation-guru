import sys
import os

# Lägg till roten i path så vi hittar backend.constants
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.fastmcp import FastMCP
import lancedb
from backend.constants import VECTOR_DATABASE_PATH

# Skapa servern
mcp = FastMCP("The Librarian")

# Initiera db
try:
    db = lancedb.connect(uri=VECTOR_DATABASE_PATH)
except Exception as e:
    print(f"Warning: Could not connect to LanceDB at {VECTOR_DATABASE_PATH}: {e}")
    db = None

@mcp.tool()
def search_documents(query: str, k: int = 3) -> str:
    """
    Search the vector database for documentation matching the query.
    Returns formatted string with filename and content.
    """
    if db is None:
        return "Database connection error."
        
    try:
        tbl = db["documentation"]
        results = tbl.search(query=query).limit(k).to_list()
        
        formatted_results = []
        for result in results:
            formatted_results.append(f"""
    Filename: {result["filename"]},
    Filepath: {result["filepath"]},
    Content: {result["content"]}
    """)
        return "\n\n---\n\n".join(formatted_results)
        
    except KeyError:
        return "Error: The 'documentation' table does not exist. Please run ingestion first."
    except Exception as e:
        return f"Database search error: {e}"

@mcp.tool()
def list_files() -> str:
    """List all available file names in the database."""
    if db is None:
        return "Database connection error."

    try:
        tbl = db["documentation"]
        df = tbl.to_pandas()
        
        if df.empty:
            return "The database is empty."
            
        unique_files = df["filename"].unique()
        return ", ".join(unique_files)
        
    except KeyError:
        return "Database table not found."
    except Exception as e:
        return f"Error listing files: {e}"

if __name__ == "__main__":
    mcp.run()