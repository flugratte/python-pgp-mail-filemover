#!/bin/bash

docker build -t python-pgp-mail-receiver . && \
 docker run --rm python-pgp-mail-receiver