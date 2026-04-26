#!/bin/bash
set -e

export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/usr/local/hadoop
export SPARK_HOME=/usr/local/spark
export PATH=/Users/timofeytst/.ya/tools/v4/11640438695/bin:/Users/timofeytst/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/opt/pmk/env/global/bin:/usr/local/munki:/Applications/iTerm.app/Contents/Resources/utilities:/Users/timofeytst/.ya/tools/v4/11640438695/bin:/Users/timofeytst/.cache/lm-studio/bin:/Users/timofeytst/.cache/lm-studio/bin:/Users/timofeytst/arcadia/marvel/gena/shuk/plugins/claude-limits/bin:/bin:/sbin:/bin

echo '--- Elasticsearch ---'
if curl -s localhost:9200 > /dev/null 2>&1; then
  echo 'already running'
else
  ~/elasticsearch-7.17.0/bin/elasticsearch -d -p ~/elasticsearch.pid
  sleep 5
  curl -s localhost:9200 > /dev/null && echo 'ok' || echo 'ERROR'
fi

echo '--- Kibana ---'
if curl -s localhost:5601 > /dev/null 2>&1; then
  echo 'already running'
else
  nohup ~/kibana-7.17.0-linux-x86_64/bin/kibana > ~/kibana.log 2>&1 &
  echo 'started (takes ~30s to be ready)'
fi

echo '--- Neo4j ---'
sudo systemctl start neo4j
systemctl is-active neo4j

echo '--- HDFS ---'
if hdfs dfsadmin -report 2>/dev/null | grep -q 'Live datanodes'; then
  echo 'already running'
else
  start-dfs.sh
fi
hdfs dfsadmin -report 2>/dev/null | grep 'Live datanodes'

echo '--- PostgreSQL ---'
sudo systemctl start postgresql
systemctl is-active postgresql

echo ''
echo 'All services started.'
