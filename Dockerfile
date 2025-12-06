FROM python:3.11

WORKDIR /backend

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY backend/ ./  # <-- this puts contents of your repo's backend folder into /backend in container

CMD ["python", "app.py"]
