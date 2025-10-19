FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/reports /app/data

EXPOSE 8000

CMD ["python", "src/secure_api.py"]