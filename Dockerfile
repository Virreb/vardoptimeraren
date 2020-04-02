FROM python:3.8-slim-buster
RUN apt-get update

# Create folder and copy all files and folders except for those in .dockerignore
RUN mkdir /hack-the-crisis/
COPY . /hack-the-crisis/
WORKDIR /hack-the-crisis

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-c", "src/webapp/gunicorn.conf.py", "src.webapp.wsgi:server"]
