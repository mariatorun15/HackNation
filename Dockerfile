FROM python:3.11

WORKDIR /backend

RUN apt-get update && apt-get install -y poppler-utils


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./

CMD ["python", "app.py"]
