import os

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "CarrionTorres1"
MYSQL_DB = "telegram"

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "host.docker.internal")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")