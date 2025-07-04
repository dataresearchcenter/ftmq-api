export LOG_LEVEL ?= info
export COMPOSE ?= docker-compose.yml
export NOMENKLATURA_DB_URL = sqlite:///nomenklatura.db

api: nomenklatura.db
	FTMQ_API_CATALOG=./tests/fixtures/catalog.json DEBUG=1 uvicorn ftmq_api.api:app --reload --port 5000

nomenklatura.db:
	poetry run ftmq -i ./tests/fixtures/ec_meetings.ftm.json -o $(NOMENKLATURA_DB_URL)
	poetry run ftmq -i ./tests/fixtures/eu_authorities.ftm.json -o $(NOMENKLATURA_DB_URL)
	poetry run ftmq -i ./tests/fixtures/gdho.ftm.json -o $(NOMENKLATURA_DB_URL)
	cat ./tests/fixtures/*.ftm.json | poetry run ftmqs transform | poetry run ftmqs --uri $(NOMENKLATURA_DB_URL) index

test: nomenklatura.db
	poetry run pytest -s --cov=ftmq_api --cov-report lcov -v

typecheck:
	# pip install types-python-jose
	# pip install types-passlib
	# pip install pandas-stubs
	poetry run mypy ftmq_api

lint:
	poetry run flake8 ftmq_api --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run flake8 ftmq_api --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

docker:
	docker-compose -f $(COMPOSE) up -d

redis:
	docker run -p 6379:6379 redis

clean:
	rm -rf nomenklatura.db

documentation:
	mkdocs build
	aws --profile nbg1 --endpoint-url https://s3.investigativedata.org s3 sync ./site s3://docs.investigraph.dev/lib/ftmq-api
