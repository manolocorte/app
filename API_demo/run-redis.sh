#!/bin/bash
if [ ! -d redis-stable/src ]; then
    tar xvzf redis-stable.tar.gz
    rm redis-stable.tar.gz
fi
cd redis-stable
make
src/redis-server &
