# Use an official Python runtime as a parent image
FROM python:3.12.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]