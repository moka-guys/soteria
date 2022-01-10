# Soteria

> The greek goddess of safety and salvation

Simple flask web server that validates files and suggests changes.

## Illumina SampleSheet Upload App

Validates uploaded samplesheets and places them in the correct location. The samplesheet is only uploaded if it passes all 
checks. Displays the results of the checks to the user. Has user registration, login, logout and password reset 
functionality.

## Running the webapp
The webapp can be run in either development, testing or production mode. Development mode involves using the repository 
as is. Testing and production mode involve running the script within a docker container and supplying the correct 
volumes.

### Development mode
***DEBUG should be set to True in the config***

In development mode, the script is run as is to enable changes to be easily made to the scripts.

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
4. Initialise the database, and run the flask app: 
```
python3 soteria/manage.py
python3 soteria/views.py
```
### Test and production mode
***DEBUG should be set to False in the config file***

The app should be packaged into a docker image using the Dockerfile.
1. Clone the repository and run the following commands to create the docker image:
```
sudo docker build -t soteria:v1.0 -f Dockerfile /usr/local/src/mokaguys
```
When running the container:
* -p specifies the ports
* -u specifies the user and group (1000 being moka-guys, 0 being root) - this ensures the database is created with 
permissions that allow the webapp to write to the database
* -v specifies the bind mounts, i.e. the directories on the host that are mounted into the container

The following are provided as volumes to the docker container:
* Directory containing the database/migrations
* Samplesheets directory

These volumes are provided with read and write permissions as this is required for the samplesheet checks and upload, 
as well as for reading and writing to the database. As the directory containing the database/migrations is provided as
a volume therefore stored outside the docker image, re-running the docker will use the existing database/migrations (no 
risk of overwriting).

Running manage.py creates the database, views.py to runs the app.

#### Testing mode
Run the docker image ensuring the correct testing mount points are supplied as below:
``` 
docker run -p 3333:3333 -v /usr/local/src/mokaguys/development_area/soteria/samplesheets:/mokaguys/development_area/soteria/samplesheets/ -v /usr/local/src/mokaguys/development_area/soteria/soteria:/mokaguys/development_area/soteria/soteria -u 1000:0 soteria:v1.0 manage.py
docker run -p 3333:3333 -v /usr/local/src/mokaguys/development_area/soteria/samplesheets:/mokaguys/development_area/soteria/samplesheets/ -v /usr/local/src/mokaguys/development_area/soteria/soteria:/mokaguys/development_area/soteria/soteria -u 1000:0 soteria:v1.0 views.py
```
#### Production mode
Run the docker image ensuring the correct (production) mount points are supplied as below:
```
docker run -p 3333:3333 -v /media/data3/share/samplesheets:/mokaguys/development_area/soteria/samplesheets/ -v /usr/local/src/mokaguys/apps/soteria/soteria:/mokaguys/development_area/soteria/soteria/ -u 1000:0 soteria:v1.0 manage.py
docker run -p 3333:3333 -v /media/data3/share/samplesheets:/mokaguys/development_area/soteria/samplesheets/ -v /usr/local/src/mokaguys/apps/soteria/soteria:/mokaguys/development_area/soteria/soteria/ -u 1000:0 soteria:v1.0 views.py
```