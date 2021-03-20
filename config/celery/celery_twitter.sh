#!/usr/bin/env bash

VIRTUALENV_BIN=/home/ubuntu/virtual_env/mnemonic/bin
cd /home/ubuntu/Mnemonic
source $VIRTUALENV_BIN/activate && source $VIRTUALENV_BIN/postactivate

echo "${1-start}ing celery twitter"
DJANGO_SETTINGS_MODULE=mnemonic.core.settings $VIRTUALENV_BIN/celery multi ${1} \
    1 \
	-A mnemonic.core \
    --pidfile=pids/celery/twitter.%N.pid \
    --hostname=celery_twitter_%i@%h \
	-l INFO \
	--logfile=logs/celery/twitter.%N.log \
    --without-gossip --without-mingle --without-heartbeat \
    --max-tasks-per-child=1 \
    --pool=solo \
    -Q:1 T_crawl_twitter \
    -c:1 1
