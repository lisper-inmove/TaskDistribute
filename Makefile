dev:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && APPROOT=`pwd`/src uvicorn src.app:app --reload
dev-consumer:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && APPROOT=`pwd`/src python src/scheduler/main.py
test:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && python src/test.py

api:
	cd src/proto && make api-python
entity:
	cd src/proto && make entity

dev-redis:
	source bin/util.sh && MQ_TYPE=REDIS uvicorn src.app:app --reload
dev-kafka:
	source bin/util.sh && MQ_TYPE=KAFKA uvicorn src.app:app --reload
dev-pulsar:
	source bin/util.sh && MQ_TYPE=PULSAR uvicorn src.app:app --reload

test-redis:
	source bin/util.sh && python src/test/redis-mq.py
test-kafka:
	source bin/util.sh && python src/test/kafka-mq.py
test-pulsar:
	source bin/util.sh && python src/test/pulsar-mq.py
