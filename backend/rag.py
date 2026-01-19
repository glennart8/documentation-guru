import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.google import GoogleModel
from backend.data_models import RagResponse

# --- IMPORTERA FRÅN SERVRARNA ---
from mcp_servers.tts_server import speak_text
from mcp_servers.knowledge_server import search_documents, list_files

# fallback-kedja
model = FallbackModel(
    GoogleModel("gemini-2.5-flash", provider="google-gla"),
    GoogleModel("gemini-2.0-flash", provider="google-gla"),
    GoogleModel("gemini-1.5-flash", provider="google-gla"),
)

rag_agent = Agent(
    model=model,
    retries=2,
    system_prompt=(
        "You are a 'Documentation Guru', an expert software engineering assistant focused on PydanticAI, LangChain, and Python.",
        "Your task is to answer technical questions and provide working code examples based strictly on the retrieved documentation.",
        "If the user asks about a specific library version or feature, verify it against the retrieved context.",
        "Don't hallucinate. If the answer isn't in the context, state that you cannot find the information in the available documentation.",
        "Keep answers technical, structured, and helpful for developers. Include the source filename for reference.",
        "If the user asks you to speak, read aloud, or give a verbal summary, use the 'speak' tool immediately."
    ),
    output_type=RagResponse,
)

# WRAPPERS FÖR VERKTYGEN
# Hämta de 3 bäst matchande dokumenten
@rag_agent.tool_plain
def retrieve_top_documents(query: str, k=3) -> str:
    """
    Uses vector search to find the closest k matching documents to the query.
    """
    return search_documents(query, k)

# Visa alla dokument
@rag_agent.tool_plain
def list_available_documents() -> str:
    """
    List all file names currently in the database. 
    Use this when the user asks what documents are available.
    """
    return list_files()

# Läs upp
@rag_agent.tool_plain
async def speak(text: str) -> str:
    """
    Reads the provided text aloud using an AI voice.
    Use this tool when the user explicitly asks you to speak.
    """
    return await speak_text(text)