# Runbook: Запуск аналитической системы "Интернет-магазин"

> Все команды выполняются на сервере:
> ```bash
> ssh timofeytst@158.160.202.75
> cd ~/shop-analytics
> source venv/bin/activate
> ```
> Переменные окружения Spark/Hadoop нужны для команд spark-submit:
> ```bash
> export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
> export HADOOP_HOME=/usr/local/hadoop
> export SPARK_HOME=/usr/local/spark
> export PATH=$PATH:$HADOOP_HOME/bin:$SPARK_HOME/bin
> ```

---

## Elasticsearch

**Пересоздать индексы и переиндексировать** (нужно при изменении данных):
```bash
python elasticsearch/create_index.py   # удаляет старые индексы и создаёт новые
python elasticsearch/index_docs.py     # загружает 2030 покупок и 2030 товаров
```

**Запустить запросы (агрегации)**:
```bash
python elasticsearch/queries.py        # выводит результаты в терминал
```

**Kibana UI** — в отдельном терминале на локальной машине:
```bash
ssh -L 5601:localhost:5601 timofeytst@158.160.202.75
```
→ [http://localhost:5601](http://localhost:5601)

---

## Neo4j

**Загрузить граф из ES** (при повторном запуске очищает граф сам):
```bash
python neo4j/load_graph.py             # DETACH DELETE всех узлов, затем создаёт заново
```

**Запустить запрос (топ покупатель)**:
```bash
python neo4j/query.py
```

**Neo4j Browser** — в отдельном терминале:
```bash
ssh -L 7474:localhost:7474 -L 7687:localhost:7687 timofeytst@158.160.202.75
```
→ [http://localhost:7474](http://localhost:7474) (логин: `neo4j` / `neo4j123`)

Вставить запрос вручную в браузере:
```cypher
MATCH (p:Purchase)-[r:INCLUDES]->(t:Product)
WITH p.customer_info AS customer, sum(r.total_price) AS total_spent
ORDER BY total_spent DESC LIMIT 1
RETURN customer, total_spent
```

---

## Spark

**Создать CSV и сохранить в HDFS** (при повторном запуске перезаписывает):
```bash
spark-submit --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 spark/create_csv.py
```

**Запустить SQL-запрос + сбор данных монитора**:
```bash
spark-submit --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 spark/query.py
```
> Результаты монитора сохраняются в `spark/monitor_results.json`

**Spark UI (Monitor)** — запустить `spark-submit`, затем сразу в другом терминале на локальной машине:
```bash
ssh -L 4040:localhost:4040 timofeytst@158.160.202.75
```
→ [http://localhost:4040](http://localhost:4040)  
> UI доступен только пока `spark-submit` работает

**Проверить содержимое HDFS**:
```bash
/usr/local/hadoop/bin/hdfs dfs -ls /shop-analytics/
```

---

## Pgvector

**Создать эмбеддинги и загрузить в БД** (при повторном запуске — TRUNCATE + перезапись):
```bash
OPENAI_API_KEY=sk-... python pgvector/vectorize.py
```
> ~2030 запросов к OpenAI API, занимает 1-2 минуты

**Запустить запрос поиска 3 ближайших документов**:
```bash
python pgvector/query.py
```

---

## Очистка при повторном запуске

| Система     | Нужна ручная очистка? | Что происходит автоматически                        |
|-------------|----------------------|-----------------------------------------------------|
| Elasticsearch | **Нет** | `create_index.py` удаляет и пересоздаёт индексы    |
| Neo4j       | **Нет** | `load_graph.py` делает `DETACH DELETE` перед загрузкой |
| Spark HDFS  | **Нет** | `create_csv.py` пишет с `mode="overwrite"`          |
| Pgvector    | **Нет** | `vectorize.py` делает `TRUNCATE TABLE` перед вставкой |

Если всё же нужно очистить вручную:
```bash
# Elasticsearch — удалить индексы
curl -X DELETE localhost:9200/purchases
curl -X DELETE localhost:9200/products

# Neo4j — очистить граф
python -c "
from neo4j import GraphDatabase
d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','neo4j123'))
with d.session() as s: s.run('MATCH (n) DETACH DELETE n')
print('Graph cleared')
"

# Spark — удалить данные из HDFS
hdfs dfs -rm -r /shop-analytics/customers /shop-analytics/purchases /shop-analytics/products

# Pgvector — очистить таблицу
sudo -u postgres psql -d shop_analytics -c "TRUNCATE TABLE purchase_vectors;"
```
