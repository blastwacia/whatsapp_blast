from flask import Flask, request, render_template, jsonify
import pandas as pd
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
from time import sleep
from random import randint
import re
from werkzeug.utils import secure_filename
import logging

# Initialize Flask app
app = Flask(__name__)

# Folder Upload Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# Global Variables (Session-safe)
sent_numbers = []
failed_numbers = []
last_sent_index = 0
driver = None

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Helper functions
def allowed_file(filename):
    """Check if the file is a valid CSV."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_number(nomor):
    """Check if the phone number is valid."""
    pattern = r'^\+62\d{8,15}$'
    return re.match(pattern, nomor) is not None

# Routes
@app.route("/")
def index():
    return render_template("index.html")  # Ensure index.html exists in templates folder

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part in request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected."}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        return jsonify({"status": "success", "message": f"File {filename} uploaded successfully.", "file_path": file_path})
    else:
        return jsonify({"status": "error", "message": "Invalid file type. Only CSV allowed."}), 400

@app.route("/start", methods=["POST"])
def start_blasting():
    global sent_numbers, failed_numbers, last_sent_index, driver

    # Check if request is in JSON format
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be in JSON format."}), 400

    # Parse JSON data from request
    request_data = request.get_json()
    file_path = request_data.get("file_path")
    message_template = request_data.get("message", "").strip()

    # Validate file path and message
    if not file_path or not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "Uploaded file not found."}), 400
    if not message_template:
        return jsonify({"status": "error", "message": "Message cannot be empty."}), 400

    try:
        # Initialize WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        
        # Path to chromedriver
        service = Service(executable_path="chromedriver")  # Adjust this if necessary
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Load WhatsApp Web
        driver.get("https://web.whatsapp.com")
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//div[@id='app']")))

        # Process CSV file
        try:
            data = pd.read_csv(file_path, dtype={"NO HANDPHONE": str}).dropna(subset=["NO HANDPHONE"])
            data["NO HANDPHONE"] = data["NO HANDPHONE"].apply(lambda x: x.strip())
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            return jsonify({"status": "error", "message": "Error processing the uploaded CSV file."}), 400

        # Send messages to numbers
        for index, row in data.iloc[last_sent_index:].iterrows():
            nomor = row["NO HANDPHONE"]
            if not is_valid_number(nomor):
                failed_numbers.append(nomor)
                continue

            pesan = message_template.replace("{USER_ID}", row.get("USER ID", "Unknown"))
            try:
                pesan_encoded = urllib.parse.quote(pesan)
                url = f"https://web.whatsapp.com/send?phone={nomor}&text={pesan_encoded}"
                driver.get(url)
                sleep(5)

                # Wait for the send button and click
                tombol_kirim = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
                )
                tombol_kirim.click()
                sent_numbers.append(nomor)
                last_sent_index += 1
            except Exception as e:
                failed_numbers.append(nomor)
                logger.error(f"Error sending to {nomor}: {str(e)}")

            # Random sleep to avoid detection
            sleep(randint(90, 180))

        # Close WebDriver and complete process
        driver.quit()
        return jsonify({"status": "success", "message": "Blasting completed."})

    except Exception as e:
        if driver:
            driver.quit()
        logger.error(f"Error during blasting process: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({
        "sent_numbers": sent_numbers,
        "failed_numbers": failed_numbers,
        "last_sent_index": last_sent_index
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
