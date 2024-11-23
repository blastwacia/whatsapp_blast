# Gunakan image dasar Python
FROM python:3.9-slim

# Menginstal dependensi untuk menjalankan Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libxss1 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Mengunduh dan mengekstrak chromedriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q --no-check-certificate https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin \
    && rm chromedriver_linux64.zip

# Menginstal Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get install -f

# Install dependensi Python yang diperlukan
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Salin seluruh aplikasi Flask ke dalam kontainer
COPY . /app

# Tentukan port yang digunakan oleh aplikasi
EXPOSE 5000

# Menjalankan aplikasi Flask
CMD ["python", "app.py"]
