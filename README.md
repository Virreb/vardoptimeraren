# Vårdoptimeraren
This project was created as a submission to the 
[Swedish Hack the Crisis hackaton](https://www.hackthecrisis.se/) 
and in response to the global COVID-19 
healthcare crisis.

See http://vårdoptimeraren.se/ for the full project proposal and demo.

The homepage also gathers deliverables and our thoughts as 
to how the solution could be put to use in reality.

**Mobile version is not fully functioning yet, use a desktop meanwhile.**

## The problem
Perhaps the most important challenge we face right now is how to 
ensure that all our hospitals have access to an adequate amount of 
equipment and resources. Researchers suggest that a lack of ICU-beds, 
ventilators and protective gears could mean a tenfold increase in 
COVID-19 mortality rate. 

## The solution
Vårdoptimeraren is a two-pronged approach for ensuring that all 
Swedish COVID-19 patients have access to the healthcare they need. 
By first applying machine learning to forecast the amount of future 
ICU cases in each Swedish region, we can see where to expect shortages. 
We then apply mathematical decision optimization techniques to get 
suggestions for the mathematically optimal way to move patients between 
regions in order to avoid local shortages and save lives. 

## Run the web app locally
You need to have a installation of 
[CPLEX](https://www.ibm.com/se-en/analytics/cplex-optimizer) 
in order for the optimization to work. We will soon have an 
implementation of the open-source optimization API  
[PuLP](https://coin-or.github.io/pulp/) ready aswel.

### Docker approach
If you have a CPLEX-installer for Linux and want to create a Docker 
image for the solution, put the installer in the config-folder
and change the Dockerfile accordingly.

Then build the Docker image with the Dockerfile in root folder.

> docker build -t hack-the-crisis .

and run it

> docker run -itp 5000:5000 hack-the-crisis

### Local linux environment
If you already have CPLEX installed locally. 
Create a virtual environment and install the python packages listen in 
requirements.txt

Start the web server with:

> gunicorn -c src/webapp/gunicorn.conf.py src/webapp/wsgi.py 


## Push to container registry
For Azure Container Registry: 
Use credentials in the Azure Portal-Container Registry-Access keys

> docker login CONTAINER-REGISTRY

Tag your image with your container registry

> docker tag hack-the-crisis CONTAINER-REGISTRY/hack-the-crisis:latest

Then push it!
> docker push CONTAINER-REGISTRY/hack-the-crisis:latest

Use whatever service to run your Docker container.
