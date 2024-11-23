# Gunakan image dasar Ubuntu
FROM ubuntu:20.04

# Set zona waktu secara non-interaktif
ENV DEBIAN_FRONTEND=noninteractive

# Install dependensi yang diperlukan
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

# Pastikan lokasi binary Google Chrome
RUN if [ -f "/usr/bin/google-chrome-stable" ]; then \
        ln -s /usr/bin/google-chrome-stable /usr/bin/google-chrome; \
    elif [ -f "/opt/google/chrome/google-chrome" ]; then \
        ln -s /opt/google/chrome/google-chrome /usr/bin/google-chrome; \
    fi

# Verifikasi pemasangan Google Chrome
RUN which google-chrome && google-chrome --version

# Bersihkan cache APT untuk mengurangi ukuran image
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Tambahkan file aplikasi Anda ke dalam kontainer (opsional)
# COPY . /app

# Jalankan perintah default (opsional)
CMD ["bash"]
