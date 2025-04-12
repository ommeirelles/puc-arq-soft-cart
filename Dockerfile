# Use an official Python runtime as a parent image
FROM python:latest

RUN useradd -ms /bin/sh -u 1001 app

RUN mkdir -m 777 -p /app/db

USER app

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=app:app . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

VOLUME /app/db

CMD ["python", "./src/main.py" ]