FROM python:3.11-slim

WORKDIR /NMDownloader

COPY requirements.txt .

# additionals packages
RUN apt-get update && apt-get install -y gcc g++ unar

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
