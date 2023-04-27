FROM python:3.11.3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY clean_registry.py .

CMD [ "python", "clean_registry.py" ]