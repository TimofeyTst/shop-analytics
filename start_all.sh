#!/bin/bash

HADOOP_BIN=/usr/local/hadoop/bin/hdfs
HADOOP_SBIN=/usr/local/hadoop/sbin

export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

echo "--- Elasticsearch ---"
if curl -s localhost:9200 > /dev/null 2>&1; then
  echo "already running"
else
  ~/elasticsearch-7.17.0/bin/elasticsearch -d -p ~/elasticsearch.pid
  sleep 5
  curl -s localhost:9200 > /dev/null && echo "ok" || echo "ERROR"
fi

echo "--- Kibana ---"
if curl -s localhost:5601 > /dev/null 2>&1; then
  echo "already running"
else
  nohup ~/kibana-7.17.0-linux-x86_64/bin/kibana > ~/kibana.log 2>&1 &
  echo "started (takes ~30s to be ready)"
fi

echo "--- Neo4j ---"
sudo systemctl start neo4j
systemctl is-active neo4j

echo "--- HDFS ---"
if $HADOOP_BIN dfsadmin -report 2>/dev/null | grep -q "Live datanodes"; then
  echo "already running"
else
  $HADOOP_SBIN/start-dfs.sh
  sleep 3
  $HADOOP_BIN dfsadmin -report 2>/dev/null | grep "Live datanodes"
fi

echo "--- PostgreSQL ---"
sudo systemctl start postgresql
systemctl is-active postgresql

echo ""
echo "All services started."
