FROM python:3.11-slim

WORKDIR /app

COPY app.py .

RUN pip install requests mysql-connector-python urllib3

CMD ["python", "app.py"]