#!/bin/bash

export HADOOP_HOME=/usr/local/hadoop
export PATH=/Users/timofeytst/.ya/tools/v4/11640438695/bin:/Users/timofeytst/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/opt/pmk/env/global/bin:/usr/local/munki:/Applications/iTerm.app/Contents/Resources/utilities:/Users/timofeytst/.ya/tools/v4/11640438695/bin:/Users/timofeytst/.cache/lm-studio/bin:/Users/timofeytst/.cache/lm-studio/bin:/Users/timofeytst/arcadia/marvel/gena/shuk/plugins/claude-limits/bin:/sbin

echo '--- Kibana ---'
pkill -f kibana && echo 'stopped' || echo 'was not running'

echo '--- Elasticsearch ---'
if [ -f ~/elasticsearch.pid ]; then
  kill  && echo 'stopped' || echo 'ERROR'
  rm -f ~/elasticsearch.pid
else
  pkill -f elasticsearch && echo 'stopped' || echo 'was not running'
fi

echo '--- Neo4j ---'
sudo systemctl stop neo4j && echo 'stopped'

echo '--- HDFS ---'
/usr/local/hadoop/sbin/stop-dfs.sh

echo '--- PostgreSQL ---'
sudo systemctl stop postgresql && echo 'stopped'

echo ''
echo 'All services stopped.'
