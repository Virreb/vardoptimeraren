# Vårdoptimeraren
See http://vårdoptimeraren.se/ for full proposal and demo.

## To run the web app

Install gunicorn locally and use

> gunicorn -c src/webapp/gunicorn.conf.py src/webapp/wsgi.py 

or build the dockerfile

> docker build -t hack-the-crisis .

and run it

> docker run -itp 5000:5000 hack-the-crisis

> ## To push to Azure
Use credentials in web UI under Container Registry and Access keys

> docker login <container registry>

Tag your image with your container registry

> docker tag hack-the-crisis <container registry>/hack-the-crisis:latest

Then push it!
> docker push <container registry>/hack-the-crisis:latest
