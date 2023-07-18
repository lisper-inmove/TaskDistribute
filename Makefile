dev:
	export PYTHONPATH=`pwd`/src && source bin/util.sh && APPROOT=`pwd`/src uvicorn src.app:app --reload

api:
	cd src/proto && make api-python
entity:
	cd src/proto && make entity
