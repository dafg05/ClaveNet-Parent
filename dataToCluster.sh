#!/bin/bash

DIRECTORY_TO_COPY=$1
RUN=$2

ssh hpc "mkdir -p ~/preprocessed_datasets/$RUN"
scp -r $DIRECTORY_TO_COPY hpc:~/preprocessed_datasets/$RUN