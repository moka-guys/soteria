FROM tiangolo/uwsgi-nginx-flask:python3.5-2019-10-14

LABEL author="Rachel Duffin" \
      description="Soteria v1.0" \
      maintainer="rachel.duffin2@nhs.net"

# set port the container listens on
ENV LISTEN_PORT 3333
EXPOSE 3333

# set the location of the app
# set the location of the script that runs the webapp
# set max allowed file upload size to 1MB (Nginx's default)
ENV UWSGI_INI /mokaguys/development_area/soteria/uwsgi.ini
ENV FLASK_APP = /mokaguys/development_area/soteria/run.py
ENV NGINX_MAX_UPLOAD 1m

# create apps directory to copy automate demultiplex into it
RUN cd / && \
    mkdir -p mokaguys/development_area && \
    rm -r /app

# copy in automate demultiplex, secret keys (create dummy keys for those not required)
COPY apps/automate_demultiplex /mokaguys/apps/automate_demultiplex
COPY .amazon_email_username /mokaguys/.amazon_email_username
COPY .amazon_email_pw /mokaguys/.amazon_email_pw
COPY .soteria_secretkeys /mokaguys/.soteria_secretkeys

RUN touch /mokaguys/.dnanexus_auth_token && \
    touch /mokaguys/.smartsheet_auth_token

# clone the repo, install packages, create dummy auth files
RUN apt update && \
    cd /mokaguys/development_area && \
    git clone --recurse-submodules git://github.com/moka-guys/soteria.git --branch incorporate_ss_verifier_script && \
    python3 -m pip install setuptools==43.0.0 && \
    python3 -m pip install pip==19.1.1 && \
    cd soteria && \
    python3 -m pip install -r package-requirements.txt

# workdir is used by wsgi and should be set to the application location
WORKDIR /mokaguys/development_area/soteria
