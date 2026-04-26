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

Каждый тип — 2030 документов, генерация: `generate_data.py` (faker ru_RU, seed=42).  
Покупатели: 200 уникальных, распределение покупок — Парето (20% покупателей дают 60% покупок).  
Даты: сезонные веса (декабрь ×2.0, ноябрь ×1.8, лето ×0.7).

---

## 2. Elasticsearch

### 2.1 Анализатор и маппинг (`elasticsearch/create_index.py`)

**Анализатор `russian_custom`:**
- Токенизатор `standard` — разделяет текст на слова, убирает пунктуацию
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

**Результат (фрагмент — первые 3 месяца):**
```
Total months in dataset: 24

Month: 2023-01 (98 products)
  Книга Мастер и Маргарита (мягкая обложка): 383 sold
  Книга Война и мир (подарочное издание): 408 sold
  Пылесос Dyson V15 Detect (Absolute Blue): 475 sold
  Телевизор LG 55UQ7500 (+ HDMI кабель): 197 sold
  Блендер Vitamix 5200 (+ контейнер 64oz): 142 sold

Month: 2023-02 (81 products)
  Внешний диск WD My Passport 2TB (4TB, чёрный): 242 sold
  Принтер Epson L3250 (A4, цветной): 276 sold
  Велосипед Trek Marlin 5 (2023, 29"): 250 sold
  Гантели разборные 20кг (хром): 246 sold
  Игра The Last of Us Part I PS5 (цифровой код): 121 sold

Month: 2023-03 (85 products)
  Кроссовки Nike Air Max 90 (42, красный): 303 sold
  Смартфон Samsung Galaxy A55 (8/128GB, лиловый): 156 sold
  Игровая консоль Sony PlayStation 5 (Digital Edition): 225 sold
  Игровая консоль Sony PlayStation 5 (с дисководом): 86 sold
  Йогуртница Oursson FE0205D (c таймером): 151 sold
```
Полные результаты (все 24 месяца): `elasticsearch/query_results.json`

---

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
Products in period: 155
Total revenue: 382,168,031.76 RUB
```

---

## 3. Neo4j

> Neo4j является вторичным хранилищем. Данные получаются из Elasticsearch через scroll API и загружаются в граф. Это обеспечивает консистентность: при переиндексации ES достаточно перезапустить `load_graph.py`.

### 3.1 Схема графовой БД

Узлы:
- `Purchase` — свойства: `purchase_id`, `purchase_date`, `customer_info`
- `Product` — свойства: `product_id`, `product_name`

Отношение:
- `(Purchase)-[:INCLUDES {quantity, total_price}]->(Product)`

Загрузка (`neo4j/load_graph.py`): читает все 2030 покупок из ES индекса `purchases` через `elasticsearch.helpers.scan`, очищает граф (`MATCH (n) DETACH DELETE n`), затем создаёт узлы и связи через Python driver.

**Результат:**
```
Получено из Elasticsearch: 2030 покупок
Граф очищен.
Граф заполнен: 2030 покупок.
```
Узлов Purchase: 2030, узлов Product: 120, связей INCLUDES: 2030.

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
Customer:    Давыдова Ермил Яковлевич, тел: 8 (214) 895-13-43
Total spent: 3,141,371.76 RUB
```

---

## 4. Spark

> Spark является вторичным хранилищем. Данные для CSV-таблиц получаются из Elasticsearch через scroll API (индексы `purchases` и `products`), а не из исходных JSON-файлов. Это соответствует заданию: «по данным из Elasticsearch сформировать csv-файлы».

### 4.1 Создание и заполнение таблиц (`spark/create_csv.py`)

Читает все документы из ES через `elasticsearch.helpers.scan`, строит Spark DataFrame с явной схемой, сохраняет в HDFS:

| Таблица | Поля | Строк |
|---------|------|-------|
| customers | customer_id, customer_info | 200 |
| purchases | purchase_id, customer_id, purchase_date, product_id, quantity, total_price | 2030 |
| products | product_id, product_name, unit_price | 2030 |

Путь в HDFS: `hdfs://localhost:9000/shop-analytics/{customers,purchases,products}/`

**Результат:**
```
Получено из ES [purchases]: 2030 документов
Получено из ES [products]:  2030 документов
Уникальных покупателей: 200
Уникальных товаров: 2030
Сохранено: customers → hdfs://localhost:9000/shop-analytics/customers
Сохранено: purchases → hdfs://localhost:9000/shop-analytics/purchases
Сохранено: products  → hdfs://localhost:9000/shop-analytics/products
```

### 4.2 Запрос (`spark/query.py`)

Найти покупателя и товар с максимальной стоимостью покупки:

```sql
SELECT c.customer_info, p.product_name, pu.total_price
FROM purchases pu
JOIN customers c ON pu.customer_id = c.customer_id
JOIN products  p ON pu.product_id  = p.product_id
ORDER BY pu.total_price DESC
LIMIT 1
```

**Результат:**
```
+------------------------------------------------+---------------------------------------+-----------+
|customer_info                                   |product_name                           |total_price|
+------------------------------------------------+---------------------------------------+-----------+
|Пахомов Надежда Тарасовна, тел: 8 698 169 3406  |Фотоаппарат Canon EOS R50 (kit 18-45mm)|371501.4   |
+------------------------------------------------+---------------------------------------+-----------+
```

### 4.3 Монитор (`spark/monitor_results.json`)

Данные из Spark REST API (`http://localhost:4040/api/v1/applications`).  
Всего выполнено **18 jobs**, все завершились со статусом `SUCCEEDED`.

| Job ID | Операция | Статус | Tasks |
|--------|----------|--------|-------|
| 0 | csv — read customers | SUCCEEDED | 1 |
| 1 | csv — read purchases | SUCCEEDED | 1 |
| 2–3 | count (customers, purchases) | SUCCEEDED | 1 |
| 4–5 | csv — read/write products | SUCCEEDED | 1 |
| 13–14 | showString (вывод результата) | SUCCEEDED | 1 |
| 15–17 | collect (финальный сбор данных) | SUCCEEDED | 1 |

Spark UI доступен во время выполнения: `ssh -L 4040:localhost:4040 timofeytst@158.160.202.75` → http://localhost:4040

---

## 5. Pgvector

### 5.1 Схема БД

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE purchase_vectors (
    purchase_id   INTEGER PRIMARY KEY,
    customer_info TEXT,
    embedded_text TEXT,
    embedding     vector(1536)
);
```

### 5.2 Векторизация (`pgvector/vectorize.py`)

Модель: OpenAI `text-embedding-3-small` (размерность 1536).

Данные для векторизации читаются из ES индекса `purchases`. Текст для каждого документа:
```
{customer_info}. Товар: {product_name}, количество: {quantity} шт.,
стоимость: {total_price} руб., дата: {purchase_date}
```

Батч-размер: 2048 документов на запрос. Итого: 1 батч на 2030 документов.

Запуск:
```bash
OPENAI_API_KEY=sk-... python pgvector/vectorize.py
```

### 5.3 Запрос (`pgvector/query.py`)

Найти 3 самых близких документа к покупке #1 (косинусное расстояние `<=>`):

```sql
SELECT purchase_id, customer_info, embedded_text,
       embedding <=> %s::vector AS distance
FROM purchase_vectors
WHERE purchase_id != %s
ORDER BY distance
LIMIT 3
```

**Результат:** *(будет добавлен после запуска `vectorize.py`)*

---

## 6. Команды для воспроизведения

```bash
# Подключиться к серверу
ssh timofeytst@158.160.202.75
cd ~/shop-analytics && source venv/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/usr/local/hadoop && export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin

# Elasticsearch
python elasticsearch/create_index.py   # пересоздать индексы
python elasticsearch/index_docs.py     # проиндексировать 2030×2 документов
python elasticsearch/queries.py        # выполнить агрегации

# Neo4j (читает данные из ES)
python neo4j/load_graph.py             # загрузить граф из ES
python neo4j/query.py                  # запрос топ-покупатель

# Spark (читает данные из ES)
spark-submit --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 spark/create_csv.py
spark-submit --conf spark.hadoop.fs.defaultFS=hdfs://localhost:9000 spark/query.py

# Pgvector (читает данные из ES)
OPENAI_API_KEY=sk-... python pgvector/vectorize.py
python pgvector/query.py

# SSH туннели для UI
ssh -L 5601:localhost:5601 timofeytst@158.160.202.75              # Kibana
ssh -L 7474:localhost:7474 -L 7687:localhost:7687 timofeytst@158.160.202.75  # Neo4j
ssh -L 4040:localhost:4040 timofeytst@158.160.202.75              # Spark UI
```

---

## Состояние выполнения

| Компонент | Статус |
|-----------|--------|
| Генерация данных (2030×2 документов) | ✅ |
| Elasticsearch — индексы + маппинг | ✅ |
| Elasticsearch — индексация (bulk) | ✅ |
| Elasticsearch — запросы (агрегации) | ✅ |
| Neo4j — загрузка графа из ES | ✅ |
| Neo4j — Cypher запрос | ✅ |
| Spark — CSV → HDFS из ES | ✅ |
| Spark — SQL запрос + монитор | ✅ |
| Pgvector — векторизация | ⏳ нужен OPENAI_API_KEY |
| Pgvector — поиск ближайших | ⏳ после векторизации |
