from flask import Flask, request, render_template
import os
from chatbot import read_image, read_pdf, explain_text

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

@app.route("/", methods=["GET", "POST"])
def index():
    response = ""

    if request.method == "POST":
        file = request.files["file"]
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

        if file.filename.endswith(".pdf"):
            text = read_pdf(path)
        else:
            text = read_image(path)

        response = explain_text(text)

    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)
