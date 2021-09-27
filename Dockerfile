FROM python:3.9.1-slim-buster

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip install --disable-pip-version-check -r requirements.txt

COPY app.py app.py

CMD exec gunicorn -b :8000 app:app
