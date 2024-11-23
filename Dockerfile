# Gunakan image dasar Ubuntu
FROM ubuntu:20.04

# Set zona waktu non-interaktif
ENV DEBIAN_FRONTEND=noninteractive

# Install dependensi yang diperlukan
RUN echo "Installing dependencies..." && \
    apt-get update && apt-get install -y \
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
RUN echo "Setting timezone to Asia/Jakarta..." && \
    ln -fs /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Debugging: Log untuk mengecek waktu dan status install
RUN echo "Starting to download Google Chrome..." && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    echo "Google Chrome downloaded." && \
    apt-get update && apt-get install -f -y ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb

# Periksa lokasi instalasi Google Chrome dan log hasilnya
RUN echo "Checking installation path of Google Chrome..." && \
    GOOGLE_CHROME_PATH=$(find /usr /opt -name "google-chrome*" -type f -executable | head -n 1) && \
    if [ -n "$GOOGLE_CHROME_PATH" ]; then \
        echo "Google Chrome found at: $GOOGLE_CHROME_PATH" && \
        ln -sf "$GOOGLE_CHROME_PATH" /usr/bin/google-chrome; \
    else \
        echo "Google Chrome binary not found. Installation might have failed." && exit 1; \
    fi

# Debugging: Tampilkan lokasi dan versi Google Chrome
RUN echo "Checking Google Chrome version..." && \
    which google-chrome && google-chrome --version

# Bersihkan cache APT untuk mengurangi ukuran image
RUN echo "Cleaning up APT cache..." && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Tambahkan file aplikasi Anda ke dalam kontainer (opsional)
# COPY . /app

# Debugging: Log perintah default
RUN echo "Setting default command..." 

# Jalankan perintah default (opsional)
CMD ["bash"]

