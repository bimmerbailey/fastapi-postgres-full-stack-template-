#!/bin/bash

start() {
  docker compose up backend pgadmin frontend "$@"
}

stop() {
  docker compose down
}

dump() {
  docker compose down --volumes
}

migrate() {
  docker compose run backend alembic revision --autogenerate -m "$1"
}

dev_data () {
  docker compose run --rm backend python3 app/dev_data.py
}

shell() {
  if [[ "$1" = "psql" ]]; then
    docker compose exec -it postgres psql -U postgres
  else
    docker compose exec -it "$1" /bin/sh
  fi
}

if [[ $# -eq 0 ]]; then
  start "$@"
else
  CMD=$1
  shift
  $CMD "$@"
fi