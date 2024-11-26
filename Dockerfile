# Gunakan image Python versi 3.10
FROM python:3.10-slim

# Instal dependensi sistem yang diperlukan untuk membangun numpy dan pustaka terkait
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    gfortran \
    gcc \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver

# Verifikasi instalasi ChromeDriver
RUN chromedriver --version

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

# Expose port untuk aplikasi
EXPOSE 5000

# Gunakan Gunicorn untuk menjalankan aplikasi Flask dan pastikan mendengarkan pada port yang benar
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:5000 app:app"]

RUN echo "PORT IS: $PORT"