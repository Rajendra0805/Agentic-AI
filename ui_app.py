import hashlib
import tempfile

import streamlit as st

from agent.document_loader import load_document
from agent.rag import RAGEngine
from agent.rag_agent import DocumentAgent


st.set_page_config(
    page_title="Document Analysis Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_state():
    defaults = {
        "agent": None,
        "document": None,
        "document_key": None,
        "messages": [],
        "build_error": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def build_agent(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    document_key = hashlib.sha256(file_bytes).hexdigest()

    if document_key == st.session_state.document_key:
        return

    temporary_path = None

    try:
        suffix = ".pdf" if uploaded_file.name.lower().endswith(".pdf") else ".txt"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temporary_file:
            temporary_file.write(file_bytes)
            temporary_path = temporary_file.name

        document = load_document(temporary_path)
        rag_engine = RAGEngine(document)
        agent = DocumentAgent(document, rag_engine)

        st.session_state.document = document
        st.session_state.agent = agent
        st.session_state.document_key = document_key
        st.session_state.messages = []
        st.session_state.build_error = None

    except Exception as error:
        st.session_state.document = None
        st.session_state.agent = None
        st.session_state.document_key = None
        st.session_state.build_error = str(error)


def render_sources(trace):
    evidence = trace.get("evidence", [])

    if not evidence:
        return

    with st.expander(
        f"Sources used ({len(evidence)})",
        expanded=False
    ):
        for index, item in enumerate(evidence, start=1):
            page_number = item.get("page_number", "?")
            score = item.get("rerank_score", 0)
            text = item.get("text", "").strip()

            st.markdown(
                f"**Evidence {index} · Page {page_number}**  "
                f"`rerank score: {score}`"
            )
            st.caption(text)


def render_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            trace = message.get("trace", {})
            tools = trace.get("tools", [])

            if tools:
                st.caption(
                    "Tool used: "
                    + ", ".join(tools)
                )

            render_sources(trace)


initialize_state()

st.title("Document Analysis Agent")
st.write(
    "Upload a document, then ask questions grounded in its content."
)

with st.sidebar:
    st.header("Document")
    uploaded_file = st.file_uploader(
        "Upload a PDF or text file",
        type=["pdf", "txt"]
    )

    if uploaded_file is not None:
        with st.status(
            "Preparing document...",
            expanded=False
        ):
            build_agent(uploaded_file)

    document = st.session_state.document

    if document is not None:
        st.success("Document ready")
        st.metric("Pages", len(document.get("pages", [])))
        st.caption(document.get("file_name", uploaded_file.name))
        st.caption(
            f"Indexed chunks: "
            f"{len(st.session_state.agent.rag_engine.chunks)}"
        )

    if st.button(
        "Clear conversation",
        use_container_width=True,
        disabled=st.session_state.agent is None
    ):
        st.session_state.messages = []
        st.session_state.agent.memory.clear()
        st.rerun()

    st.divider()
    st.caption(
        "The agent selects exact keyword search, semantic hybrid retrieval, "
        "or document metadata based on your question."
    )

if st.session_state.build_error:
    st.error(
        "Could not prepare the document: "
        + st.session_state.build_error
    )

if st.session_state.agent is None:
    st.info(
        "Upload a PDF or text file from the sidebar to start a conversation."
    )
else:
    for message in st.session_state.messages:
        render_message(message)

    question = st.chat_input(
        "Ask a question about the document"
    )

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        render_message(st.session_state.messages[-1])

        with st.chat_message("assistant"):
            with st.spinner("Analyzing the document..."):
                try:
                    answer = st.session_state.agent.run(question)
                    trace = dict(
                        st.session_state.agent.last_trace
                    )
                except Exception as error:
                    answer = (
                        "I could not process that question. "
                        f"Details: {error}"
                    )
                    trace = {}

            st.markdown(answer)

            tools = trace.get("tools", [])
            if tools:
                st.caption(
                    "Tool used: "
                    + ", ".join(tools)
                )
            render_sources(trace)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "trace": trace
        })
