# FROM python:3.8
FROM openjdk:8-jre
RUN apt-get update

# Create folder and copy all files and folders except for those in .dockerignore
RUN mkdir /hack-the-crisis/
COPY . /hack-the-crisis/
WORKDIR /hack-the-crisis

# RUN apt-get --yes --force-yes install default-jre
# RUN apt-get --yes --force-yes install default-jdk
RUN chmod u+x config/cplex_studio128.linux-x86-64.bin
RUN chmod u+x config/response_properties
# RUN ./config/cplex_studio129.linux-x86-64.bin -i silent
# RUN ./config/cplex_studio128.linux-x86-64.bin -i silent
RUN ./config/cplex_studio129.linux-x86-64.bin -r config/response_properties

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-c", "src/webapp/gunicorn.conf.py", "src.webapp.wsgi:server"]

# /opt/ibm/ILOG/CPLEX_Studio129
