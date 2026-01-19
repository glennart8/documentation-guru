# Documentation Guru RAG Agent

This project is a Retrieval-Augmented Generation (RAG) application designed to act as an expert software engineering assistant. It focuses on answering technical questions regarding PydanticAI, LangChain, and Python by retrieving information from a local vector database.

## Project Overview

The application consists of a Python backend utilizing PydanticAI for agent orchestration and a Streamlit frontend for the user interface. It uses a local LanceDB vector database to store and retrieve documentation chunks, ensuring answers are grounded in specific source materials.

## Features

- **RAG Architecture:** Retrieves relevant documentation using vector search before generating answers.
- **Robust AI Agent:** Implements a `FallbackModel` strategy, attempting to use Google Gemini 2.5 Flash, followed by 2.0 Flash and 1.5 Flash to ensure availability.
- **Source Citations:** The agent provides the filename and filepath of the documents used to generate the response.
- **Interactive UI:** A Streamlit web interface that maintains chat history and renders Markdown responses.

## Technical Stack

- **Language:** Python
- **AI Framework:** PydanticAI
- **Vector Database:** LanceDB
- **LLM Provider:** Google Gemini (via `google-gla`)
- **Frontend:** Streamlit

## Project Structure

- `backend/rag.py`: Contains the core logic for the PydanticAI agent, database connection, and retrieval tools (`retrieve_top_documents`, `list_available_documents`).
- `frontend/app.py`: The client-side application built with Streamlit. It handles user input, communicates with the backend API, and displays the chat history and source details.

## Setup and Usage

1. **Prerequisites:**
   - Python installed.
   - Access to Google Gemini API credentials.
   - A populated LanceDB database at the path specified in `backend.constants`.

2. **Running the Application:**
   - Ensure the backend API server is running (listening on `http://127.0.0.1:8000`).
   - Start the frontend interface:
     ```bash
     streamlit run frontend/app.py
     ```

3. **Interaction:**
   - Use the chat interface to ask technical questions. The system will query the vector database and return an answer based on the retrieved context.
