
import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import cv2

from cistercian_renderer import (
    number_to_cistercian_image,
    decode_base64_image,
    number_to_cistercian_with_segments,
)
from cistercian_recognition import recognize_cistercian_numeral

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "static/uploaded_images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert-to-cistercian", methods=["POST"])
def convert_to_cistercian():
    try:
        data = request.json
        number = int(data.get("number", 0))
        include_segments = data.get("include_segments", True)

        if number < 0 or number > 9999:
            return jsonify({"error": "Number must be between 0 and 9999"}), 400

        if include_segments:
            result = number_to_cistercian_with_segments(number)
            return jsonify({
                "image": result["image_data"],
                "number": number,
                "segments": result["segments"]
            })
        else:
            img_base64 = number_to_cistercian_image(number)
            return jsonify({"image": img_base64, "number": number})

    except ValueError:
        return jsonify({"error": "Invalid number format"}), 400
    except Exception as e:
        logger.error(f"Error converting to Cistercian: {str(e)}")
        return jsonify({"error": "An error occurred during conversion"}), 500

@app.route("/recognize-cistercian", methods=["POST"])
def recognize_cistercian():
    try:
        image = None

        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(image_path)
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        elif "imageData" in request.form:
            image_data = request.form["imageData"]
            image = decode_base64_image(image_data)

        if image is None:
            return jsonify({"error": "Could not process the image"}), 400

        result = recognize_cistercian_numeral(image)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error recognizing Cistercian: {str(e)}")
        return jsonify({"error": "An error occurred during recognition"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
