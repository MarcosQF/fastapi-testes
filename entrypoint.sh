#!/bin/sh

poetry run alembic upgrade head

poetry run uvicorn --host 0.0.0.0 fastapi_testes.main:app
