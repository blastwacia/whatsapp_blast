# Gunakan image Python versi 3.10
FROM python:3.10-slim

# Instal dependensi sistem yang diperlukan untuk membangun numpy
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    gfortran \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Setel direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt /app/

# Perbarui pip, setuptools, dan wheel
RUN pip install --upgrade pip setuptools wheel

# Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi lainnya ke dalam container
COPY . /app/

# Tentukan perintah untuk menjalankan aplikasi
CMD ["python", "app.py"]

EXPOSE 5000

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Tentukan perintah yang akan dijalankan saat container mulai
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app"]

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Gunakan Gunicorn untuk menjalankan aplikasi Flask
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:$PORT app:app"]

# Menggunakan image yang sudah mengandung Chrome dan ChromeDriver
FROM selenium/standalone-chrome:latest

# Atau, jika kamu menginstal ChromeDriver secara manual:
RUN apt-get update && apt-get install -y wget unzip \
    && wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver

# Install dependencies lainnya jika perlu
RUN pip install -r requirements.txt

# Menjalankan aplikasi
CMD ["python", "app.py"]

