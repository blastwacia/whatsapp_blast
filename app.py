from flask import Flask, request, jsonify
import pandas as pd
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

# Konfigurasi WebDriver
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path='/path/to/chromedriver')  # Sesuaikan dengan path di server
    return webdriver.Chrome(service=service, options=chrome_options)

# Validasi nomor telepon
def is_valid_number(nomor):
    pattern = r'^\+62\d{8,15}$'
    return re.match(pattern, nomor) is not None

@app.route('/send-messages', methods=['POST'])
def send_messages():
    # Ambil file CSV dan pesan dari request
    file = request.files.get('file')
    message_template = request.form.get('message')

    if not file or not message_template:
        return jsonify({'status': 'error', 'message': 'File CSV dan pesan wajib diisi!'}), 400

    # Baca file CSV
    try:
        data = pd.read_csv(file, dtype={"NO HANDPHONE": str})
        data = data.dropna(subset=["NO HANDPHONE"])
        data["NO HANDPHONE"] = data["NO HANDPHONE"].apply(lambda x: x.strip())
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error membaca file: {e}'}), 400

    # Mulai pengiriman pesan
    sent_numbers = []
    failed_numbers = []
    driver = create_driver()

    try:
        driver.get("https://web.whatsapp.com")
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "app")))

        for _, row in data.iterrows():
            nomor = row["NO HANDPHONE"]
            user_id = row.get("USER ID", "Unknown")

            if not is_valid_number(nomor):
                failed_numbers.append(nomor)
                continue

            pesan = message_template.replace("{USER_ID}", user_id)
            url = f"https://web.whatsapp.com/send?phone={nomor}&text={urllib.parse.quote(pesan)}"
            driver.get(url)
            sleep(5)

            try:
                tombol_kirim = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
                )
                tombol_kirim.click()
                sent_numbers.append(nomor)
            except Exception:
                failed_numbers.append(nomor)

            sleep(randint(90, 180))

    finally:
        driver.quit()

    return jsonify({
        'status': 'success',
        'sent_numbers': sent_numbers,
        'failed_numbers': failed_numbers
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
