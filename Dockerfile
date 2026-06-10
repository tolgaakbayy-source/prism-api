FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    wget \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/TA-Lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz \
    && tar -xzf ta-lib-0.6.4-src.tar.gz \
    && cd ta-lib-0.6.4 \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib-0.6.4 ta-lib-0.6.4-src.tar.gz

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]