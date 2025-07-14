FROM python:3.11-slim

WORKDIR /NMDownloader

COPY requirements.txt .

# additionals packages
RUN apt-get update && apt-get install -y gcc g++ unrar-free

# Add symbolic link to use unrar-free as unrar
RUN ln -s /usr/bin/unrar-free /usr/bin/unrar

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
