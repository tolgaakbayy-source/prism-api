FROM python:3.14-slim

# TA-Lib için gerekli sistem kütüphanelerini yükle
RUN apt-get update && apt-get install -y \
    wget \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# TA-Lib binary'yi indir ve kur
RUN wget https://github.com/TA-Lib/ta-lib/releases/download/v0.6.0/ta-lib-0.6.0-src.tar.gz \
    && tar -xzf ta-lib-0.6.0-src.tar.gz \
    && cd ta-lib-0.6.0 \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib-0.6.0 ta-lib-0.6.0-src.tar.gz

# Python kütüphanelerini yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodu kopyala
COPY main.py .

# Port
EXPOSE 10000

# Çalıştır
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]