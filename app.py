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
import os

app = Flask(__name__)

# Konfigurasi WebDriver
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Operasikan di mode headless (tanpa GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path='/path/to/chromedriver')  # Sesuaikan dengan path chromedriver di server
    return webdriver.Chrome(service=service, options=chrome_options)

# Validasi nomor telepon
def is_valid_number(nomor):
    # Validasi format nomor dengan kode negara Indonesia
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
        data = data.dropna(subset=["NO HANDPHONE"])  # Hapus baris tanpa nomor handphone
        data["NO HANDPHONE"] = data["NO HANDPHONE"].apply(lambda x: x.strip())  # Bersihkan spasi
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error membaca file: {e}'}), 400

    # Mulai pengiriman pesan
    sent_numbers = []
    failed_numbers = []
    driver = create_driver()

    try:
        driver.get("https://web.whatsapp.com")
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "app")))  # Tunggu WhatsApp Web terbuka

        for _, row in data.iterrows():
            nomor = row["NO HANDPHONE"]
            user_id = row.get("USER ID", "Unknown")  # Ambil USER ID jika ada

            if not is_valid_number(nomor):
                failed_numbers.append(nomor)  # Jika nomor tidak valid, tambahkan ke failed_numbers
                continue

            pesan = message_template.replace("{USER_ID}", user_id)  # Ganti placeholder dengan USER ID
            url = f"https://web.whatsapp.com/send?phone={nomor}&text={urllib.parse.quote(pesan)}"
            driver.get(url)  # Arahkan ke URL pengiriman pesan WhatsApp
            sleep(5)  # Tunggu sebentar

            try:
                tombol_kirim = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
                )
                tombol_kirim.click()  # Klik tombol kirim
                sent_numbers.append(nomor)  # Tambahkan nomor ke sent_numbers
            except Exception:
                failed_numbers.append(nomor)  # Jika gagal kirim, tambahkan ke failed_numbers

            sleep(randint(90, 180))  # Tidur sejenak antara pengiriman pesan

    finally:
        driver.quit()  # Tutup driver setelah selesai

    return jsonify({
        'status': 'success',
        'sent_numbers': sent_numbers,  # Daftar nomor yang berhasil dikirim
        'failed_numbers': failed_numbers  # Daftar nomor yang gagal dikirim
    })

@app.route('/')
def home():
    return "Aplikasi WhatsApp Blast Berhasil Berjalan!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))  # Jalankan Flask di port yang sesuai
