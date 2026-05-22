import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# Create Chroma client
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection("biogas_knowledge")

model = SentenceTransformer('all-MiniLM-L6-v2')


# Read PDF
def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


# Split text into chunks
def chunk_text(text, chunk_size=300):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])

    return chunks


# Store in ChromaDB
def store_document(file_path):

    text = read_pdf(file_path)

    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):

        embedding = model.encode(chunk).tolist()

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"chunk_{i}"]
        )


# Search relevant chunks
def search(query):

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )

    return results['documents'][0]
    def ask_openai(question):

    results = search(question)

    context = "\n".join(results)

    prompt = f"""
    You are a helpful biogas assistant.

    Context:
    {context}

    Question:
    {question}

    Answer clearly and simply.
    """

    response = client_openai.chat.completions.create(

        model="gpt-3.5-turbo",

        messages=[
            {"role": "user", "content": prompt}
        ]

    )

    return response.choices[0].message.content
    