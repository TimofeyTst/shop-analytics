
Федеральное государственное бюджетное образовательное учреждение высшего профессионального образования 
«Московский государственный технический университет имени Н. Э. Баумана»


На правах рукописи

Григорьев Ю.А.


Методические указания к курсовому проекту по дисциплине «Технология параллельных систем баз данных»

«Разработка макета аналитической системы на основе баз данных NoSQL»
















Москва - 2026

 
Оглавление
1.	Цель курсового проекта	3
2.	Задание	3
3.	Требования к оформлению курсового проекта	3
3.1.	Расчётно-пояснительная записка	3
3.2.	Перечень графического (иллюстративного) материала (плакатов)	4
4.	Литература	5
5.	Приложение 1. Титульный лист и задание (для РПЗ)	7



 
Внимание! Перед выполнением курсового проекта (КП) необходимо полностью ознакомиться с  заданием и со своим вариантом проекта (варианты вышлю по почте).

1.	Цель курсового проекта

Разработать макет аналитической системы для указанного варианта предметной области с использованием баз данных NoSQL Elasticsearch, Neo4j, Hadoop+Spark, а также Pgvector.

2.	Задание

1. Установить виртуальную машину с ubuntu 20.04.3 (ubuntu-20.04.3-desktop-amd64.iso [1б]) в VirtualBox [1а] (python 3 уже предустановлен в ubuntu 20.04.3). 
Имя: Ubuntu-01. Тип: Linux. Версия: Ubuntu (64 bit) и т.д. Объём ОП – 4ГБ, Диск – 20ГБ.
2. Установить Elasticsearch, Neo4j, Hadoop+Spark, Pgvector, как это Вы делали на лабораторных работах в 1-м семестре [2а]. Можете использовать  виртуальное окружение Python [1с] (в будущем может очень пригодиться).
Примечание. Пункты 1 и 2 уже выполнены Вами в 1-м семестре при выполнении  лабораторных работ по дисциплине ТПСБД

3. Решить следующие задачи (варианты будут разосланы по ЭП):
- вручную (или автоматически) создать два json-файла c 2030 json-документами каждого типа для предметной области, указанной в Вашем варианте; в варианте для каждого документа указаны его поля,
- в Elasticsearch [3]: создать индекс с анализатором и маппингом [4], проиндексировать json-документы, разработать запросы с вложенной агрегацией [5], представить результаты в среде Kibana [6],
- в Neo4j:  по данным из Elasticsearch заполнить графовую базу данных, разработать и реализовать запрос к этой БД,
- в Spark: по данным из Elasticsearch сформировать csv-файлы c таблицами и сохранить их в файловой системе HDFS, написать запрос и реализовать его в Spark, проанализировать процесс выполнения запроса с использованием монитора,
- в Pgvector: преобразовать документы 1-го типа в векторы [11], сохранить векторы в векторной БД, найти 3 самых близких документа для какого-либо одного документа.
4. Дополнительные материалы будут выкладываться в папку «Курсовой проект 2026» на яндекс-диск [2 б].

3.	Требования к оформлению курсового проекта

3.1.	Расчётно-пояснительная записка

РПЗ должна включать следующие разделы:
Реферат.
Ведение.
Здесь необходимо описать дать краткую характеристику Elasticsearch, Neo4j, Hadoop+Spark, Pgvector описать цель КП.
1. Задание и описание варианта КП.
Привести задание и описать вариант КП.
2. Elasticsearch.
2.1. Индексация документов.
Текст описания анализатора и маппинга и его пояснение; алгоритм программы индексации документов и его пояснение. 
2.2. Запросы.
Тексты запросов и их пояснение, результаты выполнения запросов в текстовом формате и в графическом виде (Kibana).
3. Neo4j.
3.1. Создание и заполнение графовой БД.
Алгоритм программы создания и заполнения графовой БД и его пояснение.
3.2. Запрос.
Текст запроса на языке Cypher и его пояснение, результат выполнения запроса.
4. Spark.
4.1. Создание и заполнение таблиц.
Алгоритм программы создания csv-файлов с таблицами и их сохранения в HDFS, пояснение алгоритма.
4.2. Запрос.
Скрипт запроса к БД (с оператором select), пояснение, результат его выполнения. 
4.3. Монитор.
Результат анализа работы монитора, пояснение.
5. Pgvector. 
5.1. Преобразование документа в вектор. 
Алгоритм программы преобразования документа в вектор (OpenAI, см. [11]).
5.2. Запрос.
Текст запроса поиска близких документов в Pgvector. Результат поиска.
Заключение.
Список использованных источников.
Приложения: 
Привести распечатку одного (!!) json-документа каждого типа, тексты программ (обязательно с подробными комментариями !!), распечатку работы монитора Spark.

3.2.	Перечень графического (иллюстративного) материала (плакатов)
1. Название темы КП, задание, описание варианта.
2,3.  По Elasticsearch: описание анализатора и маппинга; алгоритм программы индексации документов; тексты запросов, результаты их выполнения в текстовом формате (из командной строки) и в графическом виде (пакет Kibana).
4,5. По Neo4j: алгоритм программы создания и заполнения графовой БД; текст запроса на языке Cypher, результат выполнения запроса.
5,6,7. По Spark: алгоритм программы создания csv-файлов с таблицами и их сохранения в HDFS; скрипт запроса к БД (с оператором select), результат его выполнения; результат анализа работы монитора.
8. По Pgvector: фрагмент программы преобразования документа в вектор. Запрос поиска близких документов. Результат поиска.

4.	Литература

1а. https://white55.ru/vboxubuntu.html  установка ubuntu на ВМ
1б. https://releases.ubuntu.com/20.04.3/  образ ubuntu-20.04.3-desktop-amd64.iso
1с. https://pythonchik.ru/okruzhenie-i-pakety/virtualnoe-okruzhenie-python-venv   виртуальное окружение Python (venv)
2а.  https://disk.yandex.ru/d/2n_w5n9FK_DzWA лаб.работы 2025
2б.  https://disk.yandex.ru/d/YLVQtbRioYX6lQ курсовой проект 2026

Для Elasticsearch:
3. Тут описываются какие бывают запросы к Elasticsearch, и приводится 42 примера с объяснением:
https://coralogix.com/blog/42-elasticsearch-query-examples-hands-on-tutorial/
4. Анализаторы и маппинг:
https://habr.com/ru/post/280488/
https://xakep.ru/2015/06/11/elasticsearch-tutorial/#toc01
https://kb.objectrocket.com/elasticsearch/how-to-map-an-elasticsearch-index-using-the-python-client-266 
https://medium.com/nuances-of-programming/%D0%BD%D0%B0%D1%87%D0%B0%D0%BB%D0%BE-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%8B-%D1%81-elasticsearch-%D0%B2-python-%D1%87%D0%B0%D1%81%D1%82%D1%8C-2-412796dcb213
5. Агрегация:
Тут описываются какие бывают агрегации, и как они строятся:
https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/aggregations/
Тут описываются разные виды агрегации с объяснением и примерами:
https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/metric-agg/ - metric agg
https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/bucket-agg/ - bucket agg
https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/pipeline-agg/ - pipeline agg

https://habr.com/ru/company/mailru/blog/213849/
https://github.com/elastic/elasticsearch/issues/3300
6. Kibana:
https://coderlessons.com/tutorials/bolshie-dannye-i-analitika/vyuchit-kibanu/kibana-uchebnik
7. Doc Elasticsearch 7.5 (через VPN?):
 https://www.elastic.co/guide/en/elasticsearch/reference/7.5/index.html

Для Neo4j:
8. py2neo:
https://pypi.org/project/py2neo-history/
https://community.neo4j.com/t/farewell-py2neo-what-happens-now/64419
https://web.archive.org/web/20220219134028/http://py2neo.org/2021.1
9. cypher (через VPN?):
https://neo4j.com/docs/cypher-manual/current/
http://art-in-stamps.ru/development/cypher-p45.shtml

Для Spark
10. https://spark.apache.org/documentation.html

Для преобразования контента в вектор (для работы с Pgvector)
11.
https://habr.com/en/companies/karuna/articles/809305/
https://habr.com/en/articles/781408/
https://til.simonwillison.net/llms/openai-embeddings-related-content

https://neurohive.io/ru/osnovy-data-science/word2vec-vektornye-predstavlenija-slov-dlja-mashinnogo-obuchenija/. 

Дополнительная литература:
 Для Elasticsearch:
Тут описываются параметры маппинга для самой новой версии Elasticsearch:
https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-params.html

https://alexeykalina.github.io/technologies/elasticsearch-suggesters.html
https://alexeykalina.github.io/technologies/elasticsearch-autocomplete.html
https://alexeykalina.github.io/technologies/elasticsearch-fulltextsearch.html
https://alexeykalina.github.io/technologies/elasticsearh-facets.html
ML с Elasticsearch:
https://habr.com/ru/company/galssoftware/blog/455387/
(через VPN?):
https://medium.com/@bigdataschool/%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA%D0%B0-%D0%B1%D0%BE%D0%BB%D1%8C%D1%88%D0%B8%D1%85-%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85-%D0%B2-elasticsearch-%D0%B2%D0%BE%D0%B7%D0%BC%D0%BE%D0%B6%D0%BD%D0%BE%D1%81%D1%82%D0%B8-machine-learning-%D0%B2-elk-stack-6d5e4e6e6dd0
Для Neo4j
https://habr.com/ru/post/219441/

Для Spark
https://github.com/big-data-europe/docker-hadoop-spark-workbench
https://github.com/big-data-europe/docker-spark
