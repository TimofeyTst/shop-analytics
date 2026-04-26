#!/bin/bash

HADOOP_SBIN=/usr/local/hadoop/sbin

echo "--- Kibana ---"
pkill -f kibana && echo "stopped" || echo "was not running"

echo "--- Elasticsearch ---"
if [ -f ~/elasticsearch.pid ]; then
  kill $(cat ~/elasticsearch.pid) && echo "stopped" || echo "ERROR"
  rm -f ~/elasticsearch.pid
else
  pkill -f elasticsearch && echo "stopped" || echo "was not running"
fi

echo "--- Neo4j ---"
sudo systemctl stop neo4j && echo "stopped"

echo "--- HDFS ---"
$HADOOP_SBIN/stop-dfs.sh

echo "--- PostgreSQL ---"
sudo systemctl stop postgresql && echo "stopped"

echo ""
echo "All services stopped."
