# Soteria

> The greek goddess of safety and salvation

Simple web server that validates files and suggests changes.**dd**

## Illumina SampleSheets

Validates uploaded samplesheet and places it in the right location.


## Setup 
Once the repository has been cloned, the following commands can be run to create the docker image
```
sudo docker build - < Dockerfile 
sudo docker tag <image_id> soteria:<version_number>
```

The docker image can be run in development or production mode depending on the mount points specified. 

For development:
```
docker run -p 3333:3333 -v /usr/local/src/mokaguys/development_area/soteria/samplesheets:/soteria/samplesheets -v /usr/local/src/mokaguys/apps/automate_demultiplex:/soteria/soteria/automate_demultiplex soteria:v1.0 run.py
```
For production:
```
docker run -p 3333:3333 -v /media/data3/share/samplesheets:/soteria/samplesheets -v /usr/local/src/mokaguys/apps/automate_demultiplex:/soteria/automate_demultiplex soteria:v1.0
```