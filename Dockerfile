# Gunakan image dasar Ubuntu
FROM ubuntu:20.04

# Set zona waktu secara non-interaktif
ENV DEBIAN_FRONTEND=noninteractive

# Install dependensi yang diperlukan dan alat pendukung
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set zona waktu default ke Asia/Jakarta
RUN ln -fs /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Download dan install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y && \
    rm -f google-chrome-stable_current_amd64.deb

# Link binary Chrome secara eksplisit
RUN ln -s /usr/bin/google-chrome-stable /usr/bin/google-chrome

# Verifikasi pemasangan Google Chrome
RUN google-chrome --version

# Bersihkan cache APT untuk mengurangi ukuran image
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Tambahkan file aplikasi Anda ke dalam kontainer (opsional)
# COPY . /app

# Jalankan perintah default (opsional)
CMD ["bash"]
