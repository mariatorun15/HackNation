FROM python:3.11

WORKDIR /backend

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "/backend/app.py"]
