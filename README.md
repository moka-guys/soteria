# Soteria

> The greek goddess of safety and salvation

Simple flask web server that validates files and suggests changes.

## Illumina SampleSheet Upload App

Validates uploaded samplesheets and places them in the correct location. The samplesheet is only uploaded if it passes 
all checks. Displays the results of the checks to the user. Has user registration, login, logout and password reset 
functionality. Running the app does not overwrite the app database, only creating a new one if one doesn't already 
exist.

Uses [tiangolo/uwsgi-nginx-flask:python3.5-2019-10-14](https://hub.docker.com/layers/tiangolo/uwsgi-nginx-flask/python3.5-2019-10-14/images/sha256-ae128fe52796a12d81b88205609e958339ca4512600723f76ad664fa340a2862?context=explore) base image to handle the flask app deployment.

## Running the webapp
The webapp can be run in either development, testing or production mode. Development mode involves using the repository 
as is. Testing and production mode involve running the script within a docker container (in debug or production mode 
within the docker container respectively) and supplying the correct volumes and ports.

### Development mode
***DEBUG should be set to True in the config or this won't work***

In development mode, the script is run outside docker to enable changes to be easily made.

Setup/running is as follows:

1. Navigate to the development location: /usr/local/src/mokaguys/development_area/soteria
2. Create/activate the virtual environment: 
```
virtualenv -p python3 venv
source venv/bin/activate
```
2. Install packages
```
pip3 install -r package-requirements.txt
```
4. Run the flask app (automatically creates the database)
```
python3 run.py
```
### Test and production mode
***DEBUG should be set to False in the config file or this won't work***

The app should be packaged into a docker image using the Dockerfile.
1. Clone the repository and run the following commands to create the docker image:
```
sudo docker build -t soteria:v1.0 -f Dockerfile /usr/local/src/mokaguys
```
When running the container:
* /usr/local/src/mokaguys is the build context - contains all files/directories that the Dockerfile may need to copy 
into the Docker image
* -p specifies the ports
* -v specifies the bind mounts, i.e. the directories on the host that are mounted into the container
* --name provides a name to the container to ensure we know if it is the test or prod version

The following are provided as bind mounts to the docker container:
* Database file
* Samplesheets directory

These volumes are provided with read and write permissions as this is required for the SampleSheet checks and upload, 
as well as for reading and writing to the database. 

By default, the container made from this image will listen on port 80.

#### Testing mode
In testing mode the container port 80 is mapped to the host port 3333. 

Run the docker image ensuring the correct testing mount points are supplied as below:
``` 
sudo docker run --name TEST -p 3333:80 -v /usr/local/src/mokaguys/development_area/soteria/samplesheets:/mokaguys/development_area/soteria/samplesheets/ -v /usr/local/src/mokaguys/development_area/soteria/app/database.db:/mokaguys/development_area/soteria/app/database.db soteria:v1.0
```

#### Production mode
In production mode the container port 80 is mapped to the host port 80.

Run the docker image ensuring the correct (production) mount points are supplied as below:
```
sudo docker run --name PROD -p 80:80 -v /media/data3/share/samplesheets:/mokaguys/development_area/soteria/samplesheets/ -v /usr/local/src/mokaguys/apps/soteria/app/database.db:/mokaguys/development_area/soteria/app/database.db soteria:v1.0
```