# Аналитическая система «Интернет-магазин» — Вариант 9

**Дисциплина:** Технология параллельных систем баз данных  
**Сервер:** 158.160.202.75 (Ubuntu 24.04, Python 3.12, 16 GB RAM)  
**Проект:** `~/shop-analytics/`

---

## 1. Описание варианта

Предметная область — интернет-магазин. Два типа документов:

**Purchase (Покупка):**
- `purchase_id` — идентификатор покупки
- `customer_id` — идентификатор покупателя (1–200)
- `customer_info` — ФИО + телефон покупателя *(анализируется)*
- `purchase_date` — дата покупки (2023–2024)
- `product_id` — идентификатор товара
- `product_name` — наименование товара
- `quantity` — количество единиц
- `total_price` — стоимость покупки (руб.)

**Product (Товар):**
- `product_id` — идентификатор товара
- `product_name` — наименование
- `batch_date` — дата поступления партии (2023–2024)
- `stock_quantity` — количество на складе
- `sold_quantity` — количество проданных
- `unit_price` — стоимость единицы товара (руб.)
- `description` — описание товара *(анализируется)*
- `image_url` — ссылка на изображение

Каждый тип — 2030 документов, генерация: `generate_data.py` (faker, random, seed=42).

---

## 2. Elasticsearch

### 2.1 Анализатор и маппинг (`elasticsearch/create_index.py`)

**Анализатор `russian_custom`:**
- Токенизатор: `standard` — разделяет текст на слова, убирает пунктуацию
- Фильтр `lowercase` — приводит токены к нижнему регистру
- Фильтр `russian_stop` — убирает русские стоп-слова (`_russian_`)

```json
{
  "analysis": {
    "filter": {
      "russian_stop": { "type": "stop", "stopwords": "_russian_" }
    },
    "analyzer": {
      "russian_custom": {
        "type": "custom",
        "tokenizer": "standard",
        "filter": ["lowercase", "russian_stop"]
      }
    }
  }
}
```

**Маппинг индекса `purchases`:**

| Поле | Тип | Параметры |
|------|-----|-----------|
| purchase_id | integer | — |
| customer_id | integer | — |
| customer_info | text | analyzer: russian_custom |
| purchase_date | date | format: yyyy-MM-dd |
| product_id | integer | — |
| product_name | keyword | — |
| quantity | integer | — |
| total_price | float | — |

**Маппинг индекса `products`:**

| Поле | Тип | Параметры |
|------|-----|-----------|
| product_id | integer | — |
| product_name | keyword | — |
| batch_date | date | format: yyyy-MM-dd |
| stock_quantity | integer | — |
| sold_quantity | integer | — |
| unit_price | float | — |
| description | text | analyzer: russian_custom |
| image_url | keyword | — |

Индексация: bulk API, батчами по 500 документов (`elasticsearch/index_docs.py`).  
**Результат:** purchases: 2030 docs, 0 errors; products: 2030 docs, 0 errors.

### 2.2 Запросы с вложенной агрегацией (`elasticsearch/queries.py`)

**Запрос 1:** Разбить товары по дате поступления партии с периодом 1 месяц; для каждой группы определить число проданных товаров по каждому наименованию.

```json
{
  "size": 0,
  "aggs": {
    "by_month": {
      "date_histogram": {
        "field": "batch_date",
        "calendar_interval": "month",
        "format": "yyyy-MM"
      },
      "aggs": {
        "by_product": {
          "terms": { "field": "product_name", "size": 30 },
          "aggs": {
            "total_sold": { "sum": { "field": "sold_quantity" } }
          }
        }
      }
    }
  }
}
```

**Результат (фрагмент):**
```
Total months in dataset: 24

Month: 2023-01 (78 products)
  Фотоаппарат Canon EOS R50: 475 sold
  Книга Мастер и Маргарита: 538 sold
  Электросамокат Xiaomi Pro 2: 651 sold

Month: 2023-02 (73 products)
  Кофемашина DeLonghi Magnifica: 877 sold
  Гантели разборные 20кг: 604 sold

Month: 2023-03 (83 products)
  Миксер KitchenAid Artisan: 639 sold
  Принтер Epson L3250: 396 sold
```

**Запрос 2:** Определить общую стоимость проданных товаров за последние 2 месяца (ноябрь–декабрь 2024).

```json
{
  "size": 0,
  "query": {
    "range": { "batch_date": { "gte": "2024-11-01", "lte": "2024-12-31" } }
  },
  "aggs": {
    "total_revenue": {
      "sum": {
        "script": {
          "source": "doc['sold_quantity'].value * doc['unit_price'].value"
        }
      }
    }
  }
}
```

**Результат:**
```
Products in period: 168
Total revenue: 480,347,645.04 RUB
```

---

## 3. Neo4j

### 3.1 Схема графовой БД

Узлы:
- `Purchase` — свойства: `purchase_id`, `purchase_date`, `customer_info`
- `Product` — свойства: `product_id`, `product_name`

Отношение:
- `(Purchase)-[:INCLUDES {quantity, total_price}]->(Product)`

Загрузка: чтение из `data/purchases.json`, MERGE + CREATE через Neo4j Python driver (`neo4j/load_graph.py`).  
**Загружено:** 2030 Purchase + 30 Product узлов, 2030 связей INCLUDES.

### 3.2 Запрос (`neo4j/query.py`)

Какой покупатель заплатил наибольшую суммарную стоимость за все купленные им товары:

```cypher
MATCH (p:Purchase)-[r:INCLUDES]->(t:Product)
WITH p.customer_info AS customer, sum(r.total_price) AS total_spent
ORDER BY total_spent DESC
LIMIT 1
RETURN customer, total_spent
```

**Результат:**
```
Customer:    Григорьева Флорентин Борисовна, тел: +71462360409
Total spent: 649,900.00 RUB
```

---

## 4. Spark

### 4.1 Создание и заполнение таблиц (`spark/create_csv.py`)

Из JSON-файлов сформированы 3 таблицы и сохранены в HDFS (`hdfs://localhost:9000/shop-analytics/`):

| Таблица | Поля | Строк |
|---------|------|-------|
| customers | customer_id, customer_info | 200 |
| purchases | purchase_id, customer_id, purchase_date, product_id, quantity, total_price | 2030 |
| products | product_id, product_name, unit_price | 2030 |

```
hdfs dfs -ls /shop-analytics/
→ customers/   purchases/   products/
```

### 4.2 Запрос (`spark/query.py`)

Найти покупателя и товар с максимальной стоимостью покупки:

```sql
SELECT
    c.customer_info,
    p.product_name,
    pu.total_price
FROM purchases pu
JOIN customers c ON pu.customer_id = c.customer_id
JOIN products  p ON pu.product_id  = p.product_id
ORDER BY pu.total_price DESC
LIMIT 1
```

**Результат:**
```
+----------------------------------------------------+-------------------------+-----------+
|customer_info                                       |product_name             |total_price|
+----------------------------------------------------+-------------------------+-----------+
|Королева Самсон Валентиновна, тел: +7 (879) 516-3659|Фотоаппарат Canon EOS R50|649900.0   |
+----------------------------------------------------+-------------------------+-----------+

Customer:    Королева Самсон Валентиновна, тел: +7 (879) 516-3659
Product:     Фотоаппарат Canon EOS R50
Total price: 649,900.00 RUB
```

### 4.3 Монитор

Данные из Spark REST API (`http://localhost:4040/api/v1/applications`).  
Все 18 jobs завершились со статусом `SUCCEEDED`.

| Job | Операция | Статус | Tasks |
|-----|----------|--------|-------|
| 0 | csv (read customers) | SUCCEEDED | 1 |
| 1 | csv (read purchases) | SUCCEEDED | 1 |
| 2–3 | count (customers, purchases) | SUCCEEDED | 1–2 |
| 4–5 | csv (read/write products) | SUCCEEDED | 1 |
| 13–14 | showString (результат) | SUCCEEDED | 1 |
| 15–17 | collect (финальный сбор) | SUCCEEDED | 1 |

Полные данные монитора: `spark/monitor_results.json`

---

## 5. Pgvector

*(Заполняется после запуска `pgvector/vectorize.py` с OPENAI_API_KEY)*

### 5.1 Схема БД

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE purchase_vectors (
    purchase_id   INTEGER PRIMARY KEY,
    customer_info TEXT,
    embedding     vector(1536)
);
```

### 5.2 Векторизация (`pgvector/vectorize.py`)

Модель: OpenAI `text-embedding-3-small` (размерность 1536).

Текст для векторизации каждого документа:
```
{customer_info} {product_name} количество {quantity} стоимость {total_price}
```

Батчи по 100 документов, всего 21 батч (2030 документов).

```python
client.embeddings.create(model="text-embedding-3-small", input=texts)
```

### 5.3 Запрос (`pgvector/query.py`)

Найти 3 самых близких документа к покупке #1 (косинусное расстояние `<=>`):

```sql
SELECT purchase_id, customer_info,
       embedding <=> %s::vector AS distance
FROM purchase_vectors
WHERE purchase_id != 1
ORDER BY distance
LIMIT 3
```

**Результат:** *(будет добавлен после запуска)*

---

## 6. Команды для воспроизведения

```bash
# 1. Подключиться к серверу
ssh timofeytst@158.160.202.75

# 2. Активировать venv
cd ~/shop-analytics
source venv/bin/activate

# 3. Elasticsearch: создать индексы
python3 elasticsearch/create_index.py

# 4. Elasticsearch: проиндексировать документы
python3 elasticsearch/index_docs.py

# 5. Elasticsearch: выполнить запросы
python3 elasticsearch/queries.py

# 6. Neo4j: загрузить граф
python3 neo4j/load_graph.py

# 7. Neo4j: выполнить Cypher запрос
python3 neo4j/query.py

# 8. Spark: создать CSV и сохранить в HDFS
export HADOOP_HOME=/usr/local/hadoop && export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin
spark-submit --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 spark/create_csv.py

# 9. Spark: выполнить SQL запрос
spark-submit --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 spark/query.py

# 10. Pgvector: векторизовать и сохранить (нужен OPENAI_API_KEY)
OPENAI_API_KEY="sk-..." python3 pgvector/vectorize.py

# 11. Pgvector: найти 3 ближайших
python3 pgvector/query.py

# SSH туннели для UI:
# Kibana:  ssh -L 5601:localhost:5601 timofeytst@158.160.202.75
# Neo4j:   ssh -L 7474:localhost:7474 -L 7687:localhost:7687 timofeytst@158.160.202.75
# Spark UI (во время выполнения): ssh -L 4040:localhost:4040 timofeytst@158.160.202.75
```

---

## Состояние выполнения

| Компонент | Статус |
|-----------|--------|
| Elasticsearch (индексы + индексация) | ✅ Выполнено |
| Elasticsearch (запросы) | ✅ Выполнено |
| Neo4j (загрузка графа) | ✅ Выполнено |
| Neo4j (Cypher запрос) | ✅ Выполнено |
| Spark (CSV → HDFS) | ✅ Выполнено |
| Spark (SQL запрос + монитор) | ✅ Выполнено |
| Pgvector (векторизация) | ⏳ Ожидает OPENAI_API_KEY |
| Pgvector (поиск ближайших) | ⏳ Ожидает векторизации |
