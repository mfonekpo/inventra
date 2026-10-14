.DEFAULT_GOAL := help

# Resolve paths from this Makefile, including when using make -f from elsewhere.
PROJECT_ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
ENV_FILE ?= $(PROJECT_ROOT)/.env
DBT_PROJECT_DIR ?= $(PROJECT_ROOT)/inventra_analytics
PYTHON ?= $(PROJECT_ROOT)/venv/bin/python
DBT ?= $(PROJECT_ROOT)/venv/bin/dbt

# Examples: make build SELECT=stg_branches
#           make test SELECT=stg_branches DBT_ARGS="--target dev"
SELECT ?=
DBT_ARGS ?=
DOCS_PORT ?= 8080
CMD ?= --help
SOURCE_NAME ?= inventra_raw
TABLE_NAME ?= raw_customers

DBT_RUN = "$(PYTHON)" -m dotenv -f "$(ENV_FILE)" run -- "$(DBT)"
DBT_FLAGS = --profiles-dir "$(DBT_PROJECT_DIR)" --project-dir "$(DBT_PROJECT_DIR)"
DBT_SELECT = $(if $(strip $(SELECT)),--select "$(SELECT)")

.PHONY: help up down clickhouse-up clickhouse-down deps debug parse compile \
	build run test seed snapshot list ls show clone check retry clean version \
	docs docs-generate docs-serve generate-source generate-base-model freshness source-freshness dbt

help:
	@printf '%s\n' \
		'Containers:' \
		'  make up / down          Start or stop ClickHouse' \
		'  make clickhouse-up / clickhouse-down   Aliases for up / down' \
		'dbt setup:' \
		'  make deps               Install project packages' \
		'  make debug              Check configuration and connection' \
		'  make version            Show the installed dbt version' \
		'dbt development (optional SELECT=model_name):' \
		'  make compile            Compile model SQL' \
		'  make build              Build resources and run tests' \
		'  make run / test         Run models or tests separately' \
		'  make seed / snapshot    Load seeds or run snapshots' \
		'  make list / show        List resources or preview query results' \
		'  make clone              Clone selected resources' \
		'  make parse              Parse the project' \
		'  make check              Run project checks (dbt v2)' \
		'  make retry              Retry failures from the previous run' \
		'  make source-freshness   Check configured source freshness' \
		'  make clean              Remove configured local build/package directories' \
		'Documentation:' \
		'  make generate-source    Print source YAML for the tables in schema.yaml' \
		'  make generate-base-model  Print base SQL (SOURCE_NAME=inventra_raw TABLE_NAME=raw_customers)' \
		'  make docs               Generate documentation' \
		'  make docs-serve         Serve documentation on localhost (DOCS_PORT=8080)' \
		'Examples:' \
		'  make build SELECT=stg_branches' \
		'  make test SELECT=stg_branches DBT_ARGS="--target dev"' \
		'  make generate-base-model TABLE_NAME=raw_branches' \
		'  make dbt CMD="run-operation my_macro"' \
		'All dbt commands load .env automatically. Override PYTHON/DBT for another installation.'

up:
	docker compose --env-file "$(ENV_FILE)" -f "$(PROJECT_ROOT)/containers/clickhouse/docker-compose.yaml" up --build -d

down:
	docker compose --env-file "$(ENV_FILE)" -f "$(PROJECT_ROOT)/containers/clickhouse/docker-compose.yaml" down

clickhouse-up: up
clickhouse-down: down

deps debug parse check retry clean:
	$(DBT_RUN) $@ $(DBT_FLAGS) $(DBT_ARGS)

build compile run test seed snapshot list show clone:
	$(DBT_RUN) $@ $(DBT_FLAGS) $(DBT_SELECT) $(DBT_ARGS)

ls: list

version:
	$(DBT_RUN) --version

docs: docs-generate

docs-generate:
	$(DBT_RUN) docs generate $(DBT_FLAGS) $(DBT_SELECT) $(DBT_ARGS)

docs-serve:
	$(DBT_RUN) docs serve $(DBT_FLAGS) --host 127.0.0.1 --port "$(DOCS_PORT)" $(DBT_ARGS)

# Explicit table names bypass the incompatible dbt-utils catalog lookup on ClickHouse.
generate-source:
	@dbt_source_args=$$("$(PYTHON)" -c 'import json, pathlib, sys, yaml; spec = yaml.safe_load(pathlib.Path(sys.argv[1]).read_text()); print(json.dumps({"schema_name": spec["database"], "name": "inventra_raw", "table_names": sorted(table["target"] for table in spec["tables"].values())}))' "$(PROJECT_ROOT)/schema.yaml") && \
		$(DBT_RUN) run-operation generate_source $(DBT_FLAGS) --args "$$dbt_source_args" $(DBT_ARGS)

generate-base-model:
	$(DBT_RUN) run-operation generate_base_model $(DBT_FLAGS) --args '{"source_name": "$(SOURCE_NAME)", "table_name": "$(TABLE_NAME)"}' $(DBT_ARGS)

freshness: source-freshness

source-freshness:
	$(DBT_RUN) source freshness $(DBT_FLAGS) $(DBT_SELECT) $(DBT_ARGS)

# Escape hatch for any other dbt command, e.g. make dbt CMD="run-operation my_macro".
dbt:
	$(DBT_RUN) $(CMD) $(DBT_FLAGS) $(DBT_SELECT) $(DBT_ARGS)
