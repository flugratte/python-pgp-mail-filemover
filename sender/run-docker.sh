#!/bin/bash

docker build -t python-pgp-mail-sender . \
 && docker run --rm --name python-pgp-mail-sender python-pgp-mail-sender \
