import streamlit as st
import os
import numpy as np
import faiss

from dotenv import load_dotenv
from pypdf import PdfReader
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

st.set_page_config(
    page_title="EGG Chatbot",
    layout="wide"
)

st.title("EGG Chatbot")
st.subheader("Eco Gas System AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "index" not in st.session_state:
    st.session_state.index = None


def extract_pdf_text(pdf_file):

    text = ""

    reader = PdfReader(pdf_file)

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def chunk_text(text, chunk_size=800, overlap=150):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start = end - overlap

    return chunks


def get_doc_embedding(text):

    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )

    return result["embedding"]


def get_query_embedding(text):

    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_query"
    )

    return result["embedding"]


def build_index(chunks):

    if len(chunks) == 0:
        return None

    embeddings = []

    for chunk in chunks:

        try:
            embedding = get_doc_embedding(chunk)

            embeddings.append(embedding)

        except:
            continue

    if len(embeddings) == 0:
        return None

    embeddings_array = np.array(
        embeddings
    ).astype("float32")

    dimension = len(embeddings[0])

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings_array)

    return index


def search(query, index, chunks, k=3):

    if index is None:
        return []

    query_embedding = get_query_embedding(query)

    query_array = np.array(
        [query_embedding]
    ).astype("float32")

    _, indices = index.search(query_array, k)

    results = []

    for i in indices[0]:

        if i < len(chunks):
            results.append(chunks[i])

    return results


def get_available_model():

    models = genai.list_models()

    for model in models:

        if "generateContent" in model.supported_generation_methods:

            return model.name

    return None


st.sidebar.header("Upload PDF")

pdf_file = st.sidebar.file_uploader(
    "Choose PDF",
    type=["pdf"]
)

if st.sidebar.button("Process PDF"):

    if pdf_file is not None:

        with st.spinner("Processing PDF..."):

            text = extract_pdf_text(pdf_file)

            if text.strip():

                chunks = chunk_text(text)

                st.session_state.chunks = chunks

                st.session_state.index = build_index(chunks)

                st.sidebar.success(
                    "PDF processed successfully"
                )

            else:

                st.sidebar.error(
                    "No readable text found in PDF"
                )

    else:

        st.sidebar.warning(
            "Upload a PDF first"
        )


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


user_input = st.chat_input(
    "Ask something..."
)

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):

        st.write(user_input)

    context = ""

    if (
        st.session_state.index is not None
        and len(st.session_state.chunks) > 0
    ):

        docs = search(
            user_input,
            st.session_state.index,
            st.session_state.chunks
        )

        context = "\n".join(docs[:3])

    if not context:

        context = "No PDF context available."

    prompt = f"""
You are EGG Chatbot, an Eco Gas System AI assistant.

Use the PDF context if relevant.
If there is no context, answer normally.

Context:
{context}

Question:
{user_input}
"""

    try:

        model_name = get_available_model()

        if model_name is None:
            raise Exception("No Gemini model available")

        model = genai.GenerativeModel(model_name)

        response = model.generate_content(
            prompt[:30000]
        )

        answer = response.text

    except Exception as e:

        answer = f"Error: {str(e)}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):

        st.write(answer)