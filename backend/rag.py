from pydantic_ai import Agent
from backend.data_models import RagResponse
from backend.constants import VECTOR_DATABASE_PATH
import lancedb

vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)

rag_agent = Agent(
    model="google-gla:gemini-2.5-flash",
    retries=2,
    system_prompt=(
        "You are a 'Documentation Guru', an expert software engineering assistant focused on PydanticAI, LangChain, and Python.",
        "Your task is to answer technical questions and provide working code examples based strictly on the retrieved documentation.",
        "If the user asks about a specific library version or feature, verify it against the retrieved context.",
        "Don't hallucinate. If the answer isn't in the context, state that you cannot find the information in the available documentation.",
        "Keep answers technical, structured, and helpful for developers. Include the source filename for reference.",
    ),
    output_type=RagResponse,
)

@rag_agent.tool_plain
def retrieve_top_documents(query: str, k=3) -> str:
    """
    Uses vector search to find the closest k matching documents to the query
    """
    results = vector_db["documentation"].search(query=query).limit(k).to_list()
    
    formatted_results = []
    for result in results:
        formatted_results.append(f"""
    Filename: {result["filename"]},
    Filepath: {result["filepath"]},
    Content: {result["content"]}
    """)
        
    return "\n\n---\n\n".join(formatted_results)


@rag_agent.tool_plain
def list_available_documents() -> str:
    """
    List all file names currently in the database. 
    Use this when the user asks what documents are available or what you can read.
    """
    # Hämtar alla rader som en pandas dataframe (effektivt för mindre datamängder)
    df = vector_db["documentation"].to_pandas()
    
    if df.empty:
        return "The database is empty."
        
    # Returnerar en lista med unika filnamn
    unique_files = df["filename"].unique()
    return ", ".join(unique_files)

    
    
