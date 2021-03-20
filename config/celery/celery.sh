#!/usr/bin/env bash

VIRTUALENV_BIN=/home/ubuntu/virtual_env/mnemonic/bin
cd /home/ubuntu/Mnemonic
source $VIRTUALENV_BIN/activate && source $VIRTUALENV_BIN/postactivate

/home/ubuntu/Mnemonic/config/celery/celery_news.sh ${1}
#/home/ubuntu/Mnemonic/config/celery/celery_twitter.sh ${1}
