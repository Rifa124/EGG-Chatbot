import random

responses = {
    "hello","Hi","Hey": ["Hi there!", "Hello!", "Hey!", "Heyyy 🌿 ready to talk sustainability?"],
    "biogas": ["Biogas is produced from organic waste like food scraps."],
    "food waste": ["You can dispose food waste in a biogas digester."],
    "bye": ["Goodbye!", "See you later!"]
}

print("Biogas Chatbot 🤖 (type 'bye' to exit)")

while True:
    user_input = input("You: ").lower()

    if user_input == "bye":
        print("Bot:", random.choice(responses["bye"]))
        break

    found = False
    for key in responses:
        if key in user_input:
            print("Bot:", random.choice(responses[key]))
            found = True
            break

    if not found:
        print("Bot: Sorry, I don't understand that yet.")
    import pytesseract
from PIL import Image

def read_image(file_path):
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text

def explain_text(text):
    if "food waste" in text.lower():
        return "This image relates to food waste. It can be used to produce biogas through decomposition."
    elif "biogas" in text.lower():
        return "This seems to describe a biogas system where organic matter produces gas."
    else:
        return "I found some text, but I need more training to explain it better."

        import PyPDF2

def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

