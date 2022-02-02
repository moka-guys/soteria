FROM tiangolo/uwsgi-nginx-flask:python3.6

LABEL author="Rachel Duffin" \
      description="Soteria v1.0" \
      maintainer="rachel.duffin2@nhs.net"

ENV LISTEN_PORT 8080

EXPOSE 8080

# create apps directory to copy automate demultiplex into it
RUN cd / && \
    mkdir -p mokaguys/development_area

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
    cd soteria

RUN python3 -m pip install -r package-requirements.txt ; exit 0

WORKDIR /mokaguys/development_area/soteria/soteria

# run the command to start uWSGI
#CMD ["uwsgi", "app.ini"]

#ENTRYPOINT [ "python3" ]