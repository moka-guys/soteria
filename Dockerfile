FROM python:3.4.3

LABEL author="Rachel Duffin" \
      description="Soteria v1.0" \
      maintainer="rachel.duffin2@nhs.net"

# create apps directory to copy automate demultiplex into
RUN mkdir apps

# copy in automate demultiplex, secret keys
COPY apps/automate_demultiplex /apps/automate_demultiplex
COPY .amazon_email_username /.amazon_email_username
COPY .amazon_email_pw /.amazon_email_pw
COPY .soteria_secretkeys /.soteria_secretkeys

RUN apt update && \
    cd apps && \
    git clone --recurse-submodules git://github.com/moka-guys/soteria.git --branch incorporate_ss_verifier_script && \
    python3 -m pip install setuptools==43.0.0 && \
    python3 -m pip install pip==19.1.1 && \
    cd soteria && \
    python3 -m pip install -r package-requirements.txt

WORKDIR /apps/soteria/soteria

ENTRYPOINT [ "python3" ]