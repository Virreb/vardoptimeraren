Run main.py to setup basic project structure according to the Cookie Cutter Data Science template.
https://drivendata.github.io/cookiecutter-data-science/

## To run the web app
Run src/webapp/wsgi.py for local debugging the flask web server

or install gunicorn locally and use

> gunicorn -c src/webapp/gunicorn.conf.py src/webapp/wsgi.py 

## To push to Azure
Build your image
> docker build -t advectas.azurecr.io/NEW_IMAGE_NAME:TAG .

or retag a image
Tag your image to be able to push to Azure container registry.
> docker tag CURRENT_IMAGE_NAME advectas.azurecr.io/NEW_IMAGE_NAME:TAG

Use credentials in web UI under Container Registry and Access keys
> Docker login advectas.azurecr.io

Then push it!
> docker push advectas.azurecr.io/IMAGE_NAME:TAG
