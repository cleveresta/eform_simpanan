FROM python:3.7-slim

ENV http_proxy http://inet.bni.co.id:8080
ENV https_proxy http://inet.bni.co.id:8080
ENV DEBIAN_FRONTEND noninteractive

# INSTALL TOOLS
RUN apt-get update \
    && apt-get -y install apt-utils \
    && apt-get -y install libaio-dev \
    && apt-get -y install unzip \
	&& apt-get -y install libxml2-dev \
	&& apt-get -y install libxslt-dev \
    && apt-get -y install git \
    && mkdir -p /opt/data/api \
    && mkdir -p /opt/data/oracle-instantclient\
    && mkdir -p /var/log/eform_simpanan

ADD install-instantclient.sh /opt/data
ADD instantclient-basic-linux.x64-18.5.0.0.0dbru.zip /opt/data

RUN chmod 766 /opt/data/install-instantclient.sh

WORKDIR /opt/data

ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

ENV OCI_HOME=/opt/oracle/instantclient
ENV OCI_LIB_DIR=/opt/oracle/instantclient
ENV OCI_INCLUDE_DIR=/opt/oracle/instantclient/sdk/include

# INSTALL INSTANTCLIENT AND DEPENDENCIES
RUN /opt/data/install-instantclient.sh

#COPY *.py /run/
#COPY logging_config.json /run
#COPY requirements.txt /run
#ADD wsdl_blink /run/wsdl_blink
#ADD wsdl_coreService /run/wsdl_coreService
#ADD wsdl_otp /run/wsdl_otp
#ADD wsdl_smsSender /run/wsdl_smsSender
#ADD wsdl_verijelas /run/wsdl_verijelas

RUN git clone -c http.proxy= -c http.sslVerify=false https://support:support123@gitlab.bni.co.id/kelompok-api/eform_simpanan.git --branch development /run/app
WORKDIR /run/app
RUN pip --proxy=http://inet.bni.co.id:8080 install -r requirements.txt

# EXPOSE 8000/tcp

ENV http_proxy=
ENV https_proxy=

CMD ["python", "main.py"]
