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

app = Flask(__name__)

# Global variables
file_path = None
sent_numbers = []
failed_numbers = []
last_sent_index = 0
driver = None

# Create uploads directory if not exists
if not os.path.exists("uploads"):
    os.mkdir("uploads")

@app.route('/')
def index():
    return render_template("index.html")  # Pastikan `index.html` ada di folder templates

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_path
    file = request.files.get('file')
    if file:
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)
        return jsonify({"status": "success", "message": f"File {file.filename} uploaded successfully."})
    return jsonify({"status": "error", "message": "No file selected."})

@app.route('/start', methods=['POST'])
def start_blasting():
    global sent_numbers, failed_numbers, last_sent_index, driver

    if not file_path:
        return jsonify({"status": "error", "message": "Please upload a file first."})

    # Message template
    message_template = request.json.get("message", "").strip()
    if not message_template:
        return jsonify({"status": "error", "message": "Message cannot be empty."})

    try:
        # Initialize WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        service = Service(executable_path="chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Load WhatsApp Web
        driver.get("https://web.whatsapp.com")
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, "//div[@id='app']")))

        # Process file
        data = pd.read_csv(file_path, dtype={"NO HANDPHONE": str}).dropna(subset=["NO HANDPHONE"])
        data["NO HANDPHONE"] = data["NO HANDPHONE"].apply(lambda x: x.strip())

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

                tombol_kirim = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
                )
                tombol_kirim.click()
                sent_numbers.append(nomor)
                last_sent_index += 1
            except Exception:
                failed_numbers.append(nomor)

            sleep(randint(90, 180))

        driver.quit()
        return jsonify({"status": "success", "message": "Blasting completed."})

    except Exception as e:
        if driver:
            driver.quit()
        return jsonify({"status": "error", "message": str(e)})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "sent_numbers": sent_numbers,
        "failed_numbers": failed_numbers,
        "last_sent_index": last_sent_index
    })

def is_valid_number(nomor):
    pattern = r'^\+62\d{8,15}$'
    return re.match(pattern, nomor) is not None

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)