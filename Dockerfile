# Debian 8 + buildpack-deps + python
FROM python:3-jessie

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app
WORKDIR /app

CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
