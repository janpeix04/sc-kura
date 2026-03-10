#!/bin/bash

celery -A app.celery worker -P threads --concurrency=8 --loglevel=info