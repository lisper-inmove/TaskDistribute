dev:
	export PYTHONPATH=`pwd`/src && APPROOT=`pwd`/src uvicorn src.app:app --reload

api:
	cd src/proto && make api-python
entity:
	cd src/proto && make entity
