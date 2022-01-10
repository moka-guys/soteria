FROM python:3.4.3

LABEL author="Rachel Duffin" \
      description="Soteria v1.0" \
      maintainer="rachel.duffin2@nhs.net"

# create apps directory to copy automate demultiplex into
RUN mkdir -p mokaguys/development_area

# copy in automate demultiplex, secret keys
COPY apps/automate_demultiplex /mokaguys/apps/automate_demultiplex
COPY .amazon_email_username /mokaguys/.amazon_email_username
COPY .amazon_email_pw /mokaguys/.amazon_email_pw
COPY .soteria_secretkeys /mokaguys/.soteria_secretkeys

RUN apt update && \
    cd /mokaguys/development_area && \
    git clone --recurse-submodules git://github.com/moka-guys/soteria.git --branch incorporate_ss_verifier_script && \
    python3 -m pip install setuptools==43.0.0 && \
    python3 -m pip install pip==19.1.1 && \
    cd soteria && \
    python3 -m pip install -r package-requirements.txt && \
    touch /mokaguys/.dnanexus_auth_token && \
    touch /mokaguys/.smartsheet_auth_token

WORKDIR /mokaguys/development_area/soteria/soteria

ENTRYPOINT [ "python3" ]