#!/usr/bin/env bash

VIRTUALENV_BIN=/home/ubuntu/virtual_env/mnemonic/bin
cd /home/ubuntu/Mnemonic
source $VIRTUALENV_BIN/activate && source $VIRTUALENV_BIN/postactivate

echo "${1-start}ing celery news"
DJANGO_SETTINGS_MODULE=mnemonic.core.settings $VIRTUALENV_BIN/celery multi ${1} \
    1 \
	-A mnemonic.core \
    --pidfile=pids/celery/%N.pid \
    --hostname=celery_%i@%h \
	-l INFO \
	--logfile=logs/celery/%N.log \
    --without-gossip --without-mingle --without-heartbeat \
    --pool=solo \
    -Q:1 T_crawl_feed,T_process_article \
    -c:1 1
