import streamlit as st
import requests 
from pathlib import Path

ASSETS_PATH = Path(__file__).absolute().parents[1] / "assets"

def layout():
    st.markdown("# Documentation Guru")
    st.markdown("Ask technical questions about PydanticAI, Lancedb (FTS and embeddings)")
    
    if st.button("send") and text_input != "":
        response=requests.post("http://127.0.0.1:8000/rag/query", json={"prompt": text_input})
        
        data = response.json()
        
        st.markdown("## Question:")
        st.markdown(text_input)
        
        st.markdown("## Answer:")
        st.markdown(data["answer"])
        
        with st.expander("Source Details"):
            st.markdown(f"**File:** {data['filename']}")
            st.markdown(f"**Path:** {data['filepath']}")
        
if __name__ == "__main__":
    layout()