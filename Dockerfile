FROM python:3.8-slim-buster
RUN apt-get update
WORKDIR /hack-the-crisis
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn -c src/app/gunicorn.conf.py src/app/wsgi.py"]
