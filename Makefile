web:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && APPROOT=`pwd`/src uvicorn src.app:app --reload
scheduler:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && APPROOT=`pwd`/src python src/scheduler/main.py

api:
	cd src/proto && make api-python
entity:
	cd src/proto && make entity

web-redis:
	# source bin/util.sh && MQ_TYPE=REDIS uvicorn src.app:app --reload
	source bin/util.sh && MQ_TYPE=REDIS uvicorn src.app:app --workers 8
web-redis-cluster:
	# source bin/util.sh && MQ_TYPE=REDIS uvicorn src.app:app --reload
	source bin/util.sh && MQ_TYPE=REDIS_CLUSTER uvicorn src.app:app --workers 2
web-kafka:
	# source bin/util.sh && MQ_TYPE=KAFKA uvicorn src.app:app --reload
	source bin/util.sh && MQ_TYPE=KAFKA uvicorn src.app:app --workers 8
web-pulsar:
	source bin/util.sh && MQ_TYPE=PULSAR uvicorn src.app:app --reload

scheduler-redis:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && MQ_TYPE=REDIS APPROOT=`pwd`/src python src/scheduler/main.py
scheduler-redis-cluster:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && MQ_TYPE=REDIS_CLUSTER APPROOT=`pwd`/src python src/scheduler/main.py
scheduler-kafka:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && MQ_TYPE=KAFKA APPROOT=`pwd`/src python src/scheduler/main.py
scheduler-pulsar:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && MQ_TYPE=PULSAR APPROOT=`pwd`/src python src/scheduler/main.py

test-redis:
	source bin/util.sh && python src/test/redis-mq.py
test-redis-cluster:
	source bin/util.sh && python src/test/redis-mq.py
test-kafka:
	source bin/util.sh && python src/test/kafka-mq.py
test-pulsar:
	source bin/util.sh && python src/test/pulsar-mq.py

test-produce:
	python src/test/produce.py
test-lock:
	source bin/util.sh && python src/test/redis-lock.py
