FROM python:3.11-slim

WORKDIR /app

RUN pip install flask psutil

COPY monitor.py .
COPY index.html .

RUN mkdir /data

CMD ["python","monitor.py"]
