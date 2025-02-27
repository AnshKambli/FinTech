import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import base64
import os

app = Flask(__name__)

# Set up Gemini API key
genai.configure(api_key="AIzaSyAapoREnF6dErSnRooq8391oEdySyzjn4c")

# Folder to store uploaded images
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store extracted text globally
extracted_text = ""

@app.route("/")
def chatbot():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    global extracted_text  # Store extracted text for chatbot

    if "image" not in request.files:
        return jsonify({"response": "No file uploaded."})

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"response": "No file selected."})

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)

    # Convert image to base64
    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Process the image with Gemini Vision Pro
    model = genai.GenerativeModel("gemini-pro-vision")
    response = model.generate_content([{"type": "image", "data": image_base64}])

    extracted_text = response.text if hasattr(response, "text") else "No text extracted."

    return jsonify({"response": "Image uploaded and processed. You can now ask questions based on it."})

@app.route("/", methods=["POST"])
def get_response():
    user_input = request.form["user_input"]
    model = genai.GenerativeModel("gemini-pro")

    # If text is extracted from an image, use it in the chatbot response
    if extracted_text:
        user_input = f"{user_input}\n\nBased on this financial statement:\n{extracted_text}"

    response = model.generate_content(user_input)
    bot_reply = response.text if hasattr(response, "text") else "I'm sorry, I couldn't understand that."

    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
