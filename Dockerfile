FROM python:3.7
RUN apt-get update

# Create folder for the project
RUN mkdir /hack-the-crisis/

# copy config files with cplex and install it
COPY config/ /hack-the-crisis/config
WORKDIR /hack-the-crisis/config
RUN chmod u+x cplex_studio129.linux-x86-64.bin  # make it executable
RUN ./cplex_studio129.linux-x86-64.bin  # execute

# Install the cplex python library so docplex can talk to cplex runtime
WORKDIR /opt/ibm/ILOG/CPLEX_Studio129/cplex/python/3.7/x86-64_linux
RUN python setup.py install

# copy rest of the code and data
WORKDIR /
COPY data /hack-the-crisis/data
COPY src /hack-the-crisis/src
COPY requirements.txt /hack-the-crisis/requirements.txt

# install packages
WORKDIR /hack-the-crisis
RUN pip install -r requirements.txt

# open up port for webserver
EXPOSE 5000

# when starte,d run gunicorn with config file
CMD ["gunicorn", "-c", "src/webapp/gunicorn.conf.py", "src.webapp.wsgi:server"]

# /opt/ibm/ILOG/CPLEX_Studio129
# RUN apt-get --yes --force-yes install default-jre
# RUN apt-get --yes --force-yes install default-jdk
# RUN chmod u+x config/installer.properties
# RUN ./config/cplex_studio129.linux-x86-64.bin -i silent
# RUN ./config/cplex_studio128.linux-x86-64.bin -i silent
