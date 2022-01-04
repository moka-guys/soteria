FROM python:3.9

LABEL author="Rachel Duffin" \
      description="Soteria v1.0" \
      maintainer="rachel.duffin2@nhs.net"

RUN apt-get update -y && \
    apt-get install -y apt-utils python3-pip python-dev && \
    git clone --recurse-submodules git://github.com/moka-guys/soteria.git --branch incorporate_ss_verifier_script && \
    touch /.dnanexus_auth_token && \
    touch /.amazon_email_pw && \
    touch /.smartsheet_auth_token && \
    touch /.amazon_email_username

WORKDIR /soteria

ENV STATIC_URL /soteria/static

ENV STATIC_PATH /soteria/static

RUN pip install -r package-requirements.txt

ENTRYPOINT [ "python3" ]