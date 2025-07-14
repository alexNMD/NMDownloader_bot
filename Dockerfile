FROM python:3.11-slim

WORKDIR /NMDownloader

COPY requirements.txt .

# additionals packages
RUN apt-get update && apt-get install -y gcc g++ wget tar

# Download & Install RAR package from official source
ARG UNRAR_PACKAGE="rarlinux-x64-712.tar.gz"
RUN wget https://www.rarlab.com/rar/${UNRAR_PACKAGE} && \
    tar -xzf ${UNRAR_PACKAGE} && \
    mv rar/unrar /usr/local/bin/unrar && \
    chmod +x /usr/local/bin/unrar && \
    rm -rf ${UNRAR_PACKAGE}

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
