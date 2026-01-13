import streamlit as st
import requests 
from pathlib import Path

ASSETS_PATH = Path(__file__).absolute().parents[1] / "assets"

def layout():
    st.markdown("# Documentation Guru")
    st.markdown("Ask technical questions about PydanticAI, Lancedb (FTS and embeddings)")

    # Initiera historik
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Visa historik (enkel rendering)
    for msg in st.session_state.messages:
        if msg.get("kind") == "request":
            with st.chat_message("user"):
                # Hämta textinnehållet från requesten
                for part in msg.get("parts", []):
                    if part.get("part_kind") == "user-prompt":
                        st.markdown(part.get("content"))
        elif msg.get("kind") == "response":
            with st.chat_message("assistant"):
                # Hämta textinnehållet från svaret
                for part in msg.get("parts", []):
                    if part.get("part_kind") == "text":
                        st.markdown(part.get("content"))
    
    # Input fält för chatt
    if prompt := st.chat_input("Ask a question"):
        # Visa användarens fråga direkt
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            response = requests.post(
                "http://127.0.0.1:8000/rag/query", 
                json={"prompt": prompt, "messages": st.session_state.messages}
            )
            data = response.json()
            
            # Uppdatera historik och visa svar
            st.session_state.messages = data["messages"]
            rag_response = data["rag_response"]
            
            with st.chat_message("assistant"):
                st.markdown(rag_response["answer"])
                with st.expander("Source Details"):
                    st.markdown(f"**File:** {rag_response['filename']}")
                    st.markdown(f"**Path:** {rag_response['filepath']}")
        
if __name__ == "__main__":
    layout()