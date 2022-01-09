# Soteria

> The greek goddess of safety and salvation

Simple web server that validates files and suggests changes.

## Illumina SampleSheets

Validates uploaded samplesheet and places it in the right location.


## Running the webapp
### Development mode
In development mode, the script is run outside a docker image to enable changes to be easily made to the scripts.
*TEST should be set to True in the Config*
n.b. the production samplesheet directory path specified in the config file will only work inside the docker container 
so there is no risk of accidentally writing to the live samplesheet folder in development mode. 

Setup/running is as follows:

1. Navigate to the development location: /usr/local/src/mokaguys/development_area/soteria
2. Create/activate the virtual environment: 
```
virtualenv -p python3 venv
source venv/bin/activate
```
2. Install packages]
```
pip3 install -r package-requirements.txt
```
4. Initialise the database, and run the flask app: 
```
python3 soteria/manage.py
python3 soteria/views.py
```
### Testing/production mode
The app can be packaged into a docker container which can be created using the Dockerfile. The docker image is used for
testing and production purposes (depending on the volumes provided).

*Ensure Test = False in the config file before creating the docker image.*

1. Clone the repository and then run the following commands to creat the docker image:
```
sudo docker build -t soteria:v1.0 -f Dockerfile /usr/local/src/mokaguys
```

This will not affect any existing database / migrations directory as these are not present within the repository. 
Therefore re-running the app will keep the existing database intact and continue to use this. 

The samplesheets directory and soteria directory are mounted as volumes with read and write permissions as this is 
required for the samplesheet checks and upload, as well as for reading and writing login details to the database.

When running the container:
* -p specifies the ports
* -u specifies the user and group (1000 being moka-guys, 0 being root) - this ensures the database is created with 
permissions that allow the webapp to write to the database
* -v specifies the bind mounts, i.e. the directories on the host that are mounted into the container

Running manage.py creates the database, views.py to runs the app.

#### Testing mode
Run the docker image ensuring the correct testing mount points are supplied as below:

``` 
docker run -p 3333:3333 -v /usr/local/src/mokaguys/development_area/soteria/samplesheets:/apps/soteria/samplesheets -v /usr/local/src/mokaguys/development_area/soteria/soteria:/apps/soteria/soteria -u 1000:0 soteria:v1.0 manage.py
docker run -p 3333:3333 -v /usr/local/src/mokaguys/development_area/soteria/samplesheets:/apps/soteria/samplesheets -v /usr/local/src/mokaguys/development_area/soteria/soteria:/apps/soteria/soteria -u 1000:0 soteria:v1.0 views.py
```

#### Production mode
Run the docker image ensuring the correct (production) mount points are supplied as below:
```
docker run -p 3333:3333 -v /media/data3/share/samplesheets:/apps/soteria/samplesheets -v /usr/local/src/mokaguys/apps/soteria/soteria:/apps/soteria/soteria/ soteria:v1.0 manage.py
docker run -p 3333:3333 -v /media/data3/share/samplesheets:/apps/soteria/samplesheets -v /usr/local/src/mokaguys/apps/soteria/soteria:/apps/soteria/soteria/ soteria:v1.0 views.py
```