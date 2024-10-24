# Use an official Python runtime as a parent image
FROM python:3.12.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app


RUN pip install pipenv
RUN pipenv install

COPY . .

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]