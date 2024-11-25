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
