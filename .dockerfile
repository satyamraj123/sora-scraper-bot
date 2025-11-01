FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Gunicorn will bind to $PORT (Render provides $PORT at runtime)
CMD exec gunicorn --bind 0.0.0.0:$PORT app:app
