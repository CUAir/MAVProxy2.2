#!/usr/bin/env bash

docker exec -t mavproxy_container bash -c "cd /root/mavproxy/MAVProxy/modules/server/static && npm run gulp" || \
echo "Make sure mavproxy container is running before running gulp"