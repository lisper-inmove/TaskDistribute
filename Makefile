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
