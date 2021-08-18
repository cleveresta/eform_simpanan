#!/bin/bash

unzip instantclient-basic-linux.x64-18.5.0.0.0dbru.zip -d /opt/oracle
mv /opt/oracle/instantclient_18_5 /opt/oracle/instantclient

export ORACLE_HOME="/opt/oracle/instantclient"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

export OCI_HOME="/opt/oracle/instantclient"
export OCI_LIB_DIR="/opt/oracle/instantclient"
export OCI_INCLUDE_DIR="/opt/oracle/instantclient/sdk/include"
