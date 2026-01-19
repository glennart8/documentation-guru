import streamlit as st
import requests 
from pathlib import Path
from typing import List, Dict, Any

# Konstanter
API_URL = "http://127.0.0.1:8000/rag/query"

# --- Hjälpfunktioner ---

def get_api_response(prompt: str, messages: List[Dict]) -> Dict[str, Any]:
    """Hanterar kommunikationen med backend-API:et."""
    try:
        response = requests.post(
            API_URL, 
            json={"prompt": prompt, "messages": messages}
        )
        response.raise_for_status() # Kasta fel om statuskoden inte är 200 OK
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Kunde inte nå servern: {e}")
        return {}

def render_message(role: str, content: str):
    """Enkel funktion för att skriva ut ett meddelande."""
    with st.chat_message(role):
        st.markdown(content)

def display_chat_history(messages: List[Dict]):
    """Loopar igenom och visar historiken baserat på meddelandetyp."""
    for msg in messages:
        kind = msg.get("kind")
        parts = msg.get("parts", [])
        
        # PydanticAI-strukturen kan vara djup, vi hämtar texten säkert
        content = ""
        for part in parts:
            if part.get("part_kind") in ["user-prompt", "text"]:
                content = part.get("content")
                break # Vi tar första textdelen vi hittar
        
        if kind == "request" and content:
            render_message("user", content)
        elif kind == "response" and content:
            render_message("assistant", content)

# --- Huvudlayout ---

def layout():
    st.title("Documentation Guru")
    st.caption("Ask technical questions about PydanticAI & LanceDB")

    # 1. Initiera state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Visa gammal historik
    display_chat_history(st.session_state.messages)

    # 3. Hantera ny input
    if prompt := st.chat_input("Ask a question..."):
        # Visa användarens fråga direkt (optimistisk UI)
        render_message("user", prompt)

        with st.spinner("Thinking..."):
            data = get_api_response(prompt, st.session_state.messages)
            
            if data:
                # Uppdatera state med ny historik från servern
                st.session_state.messages = data.get("messages", [])
                rag_response = data.get("rag_response", {})
                
                # Visa svaret
                with st.chat_message("assistant"):
                    st.markdown(rag_response.get("answer", "Inget svar mottogs."))
                    
                    # Visa källor snyggt
                    if rag_response.get("filename"):
                        with st.expander("🔍 Source Details"):
                            st.markdown(f"**File:** `{rag_response['filename']}`")
                            st.markdown(f"**Path:** `{rag_response['filepath']}`")

if __name__ == "__main__":
    layout()