#!/bin/bash

export FLASK_APP=api/app.py
gunicorn api.app:app
