import sys
from pathlib import Path
import streamlit.components.v1 as components

# Add the project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.embeddings import EmbeddingModel
from app.llm import generate_answer
from app.rag import build_context, build_citations, deduplicate_results
from app.qdrant_db import get_qdrant_client, search

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RELEVANCE_THRESHOLD = 0.45
RETRIEVAL_LIMIT = 5

# Set up the page layout
st.set_page_config(page_title="AI Document Assistant", page_icon="📄")


# Cache the model and DB connection so they only load once
@st.cache_resource(show_spinner=False)
def load_embedding_model():
    return EmbeddingModel()


@st.cache_resource(show_spinner=False)
def load_qdrant_client():
    return get_qdrant_client()


@st.cache_data(ttl=3600, show_spinner=False)
def get_available_documents():
    """Fetches all unique document names directly from Qdrant."""
    try:
        client = load_qdrant_client()
        unique_docs = set()
        offset = None

        # Scroll through the database to find all unique document names
        while True:
            records, offset = client.scroll(
                collection_name="documents",
                limit=1000,
                offset=offset,
                with_payload=["document"],
                with_vectors=False
            )

            for record in records:
                if record.payload and "document" in record.payload:
                    unique_docs.add(record.payload["document"])

            # Stop if we have reached the end of the database
            if offset is None:
                break

        return sorted(list(unique_docs))
    except Exception as e:
        return []

def main():
    # --- Sidebar UI ---
    with st.sidebar:
        st.header("📚 Available Documents")
        st.info(
            "This AI has been trained on the following legal texts. "
            "Ask any question, and it will cite the exact page number."
        )

        # Dynamically load and format the document names
        with st.spinner("Loading document list..."):
            available_pdfs = get_available_documents()

        if available_pdfs:
            for pdf in available_pdfs:
                # Clean up the name for a better user experience
                clean_name = pdf.replace(".pdf", "").replace("_", " ")
                st.markdown(f"- *{clean_name}*")
        else:
            st.markdown("- *No documents found in the database.*")

        st.divider()
        st.caption("Built to demonstrate end-to-end RAG adoption.")

    st.sidebar.markdown("---")
    with st.sidebar.expander("📝 Share Feedback"):
        components.iframe(
            "https://docs.google.com/forms/d/e/1FAIpQLSclbOV9u3gidbl0SCIErr4cKYnlKoTC1_sx2SLplHQkeCUarQ/viewform?embedded=true",
            height=550,
            scrolling=True
        )

    # --- Main Chat UI ---
    st.title("⚖️ AI Legal Assistant")
    st.markdown("Ask questions based on the pre-loaded court judgments and get answers with exact page citations.")

    with st.spinner("Loading AI models..."):
        embedding_model = load_embedding_model()
        qdrant = load_qdrant_client()

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if query := st.chat_input("e.g., What did the Supreme Court say about tribunals?"):

        # Add user message to chat history and display it
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Generate the assistant's response
        with st.chat_message("assistant"):
            with st.spinner("Searching legal documents..."):
                query_embedding = embedding_model.encode([query])[0]

                results = search(
                    client=qdrant,
                    query_embedding=query_embedding,
                    limit=RETRIEVAL_LIMIT,
                    score_threshold=RELEVANCE_THRESHOLD,
                )

                results = deduplicate_results(results)
                # --- PRINT TO TERMINAL FOR DEBUGGING ---
                # print(f"\n[DEBUG] User asked: {query}")
                # print(f"[DEBUG] Retrieved {len(results)} relevant chunks from Qdrant.")
                # for index, result in enumerate(results, start=1):
                #     print(f"   -> Result {index}: page {result.payload.get('page', '?')} (score={result.score:.3f})")
                # ---------------------------------------

            if not results:
                response = "The information is not available in the supplied documents."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                return

            with st.spinner("Analyzing relevant pages..."):
                context = build_context(results)
                answer = generate_answer(question=query, context=context)

                # Check if the LLM refused to answer. If it did, don't show citations.
                if "information is not available" in answer.lower():
                    final_response = answer
                else:
                    citations = build_citations(results)
                    final_response = f"{answer}\n\n---\n**Sources:**\n\n{citations}"

                st.markdown(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})


if __name__ == "__main__":
    main()