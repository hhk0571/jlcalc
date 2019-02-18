#!/usr/bin/env bash

venv/bin/gunicorn -b 0.0.0.0:8001 -w 1 main:app
