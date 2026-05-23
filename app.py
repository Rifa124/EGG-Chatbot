import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from PIL import Image
import base64
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Vision model
model = "llama-3.2-11b-vision-preview"

# Page configuration
st.set_page_config(
    page_title="EGG Chatbot",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1 {
    text-align: center;
    color: white;
}

.stChatMessage {
    border-radius: 15px;
    padding: 10px;
}

section[data-testid="stSidebar"] {
    background-color: #161A23;
}

.stChatInput input {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# Create upload folder
upload_folder = "uploads"

if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

# Sidebar
with st.sidebar:

    st.title("EGG Chatbot")

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload Image or PDF",
        type=["png", "jpg", "jpeg", "pdf"]
    )

    extracted_text = ""

    # Image handling
    if uploaded_file and uploaded_file.type.startswith("image"):

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Uploaded Image",
            use_container_width=True
        )

        save_path = os.path.join(
            upload_folder,
            uploaded_file.name
        )

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("Image uploaded successfully")

    # PDF handling
    elif uploaded_file and uploaded_file.type == "application/pdf":

        save_path = os.path.join(
            upload_folder,
            uploaded_file.name
        )

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        pdf_reader = PdfReader(save_path)

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

        st.success("PDF uploaded successfully")

        st.subheader("Extracted PDF Text")

        st.text_area(
            "PDF Content",
            extracted_text,
            height=300
        )

# Main title
st.title("EGG Chatbot")

# Chat memory
if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that can understand images and PDFs."
        }
    ]

# Show chat history
for msg in st.session_state.messages:

    if msg["role"] != "system":

        with st.chat_message(msg["role"]):

            st.write(msg["content"])

# User input
user_input = st.chat_input("Type your message")

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):

        st.write(user_input)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""

        # Image AI
        if uploaded_file and uploaded_file.type.startswith("image"):

            with open(save_path, "rb") as image_file:

                base64_image = base64.b64encode(
                    image_file.read()
                ).decode("utf-8")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_input
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                stream=True
            )

        # PDF AI
        elif uploaded_file and uploaded_file.type == "application/pdf":

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"Here is the PDF content:\n{extracted_text}"
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                stream=True
            )

        # Normal chat
        else:

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                stream=True
            )

        for chunk in response:

            if chunk.choices[0].delta.content:

                full_response += chunk.choices[0].delta.content

                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )