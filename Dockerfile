FROM python:3.11-slim

WORKDIR /src/app

RUN echo 'deb http://deb.debian.org/debian testing main' >> /etc/apt/sources.list \
    && apt-get update && apt-get install --no-install-recommends -y gcc g++ git procps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
