from pydantic import BaseModel, Field
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv
from pydantic_ai.messages import ModelMessage
from typing import List

load_dotenv()

embedding_model = get_registry().get("gemini-text").create(name="gemini-embedding-001")

# 3072 krävs för embedding-modellen som används
EMBEDDING_DIM = 3072

class Documentation(LanceModel):
    doc_id: str
    filepath: str
    filename: str = Field(description="the stem of the file i.e. without the suffix")
    content: str = embedding_model.SourceField()
    embedding: Vector(dim=EMBEDDING_DIM) = embedding_model.VectorField()
    

class Prompt(BaseModel):
    prompt: str = Field(description="prompt from user, if empty consider it as missing")
    messages: List[ModelMessage] = Field(default=[], description="Chat history")
    
    
class RagResponse(BaseModel):
    filename: str = Field(description="filenamn of retrieved file witout suffix")
    filepath: str = Field(description="absolut path to the retrieved file")
    answer: str = Field(description="answer based on the retrieved file")

class APIResponse(BaseModel):
    rag_response: RagResponse
    messages: List[ModelMessage]