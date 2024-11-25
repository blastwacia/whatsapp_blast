# Gunakan image Python versi 3.10-slim
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    gfortran \
    gcc \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

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

# Menjalankan aplikasi dengan Gunicorn pada port yang ditentukan oleh variabel lingkungan PORT
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:$PORT app:app"]

# Menyatakan bahwa container mendengarkan pada port 5000
EXPOSE 5000

RUN chromedriver --version
