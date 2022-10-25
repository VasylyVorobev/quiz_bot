#!/bin/bash


echo "Waiting for Rabbit"
while ! nc -z rabbitmq 5672; do sleep 1; done

echo "RabbitMQ Started !"

alembic upgrade head
echo "alembic upgrade"

gunicorn web.app:setup_app --bind :8000 --reload --worker-class aiohttp.GunicornUVLoopWebWorker

exec "$@"
