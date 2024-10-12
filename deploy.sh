#!/bin/bash

if ! git pull; then
  echo "Failed to pull from git"
  exit 1
fi

# setup virtual environment

if ! python3 -m venv .venv; then
  echo "Failed to create virtual environment"
  exit 1
fi

source .venv/bin/activate

if ! pip install -r requirements.txt; then
  echo "Failed to install requirements"
  exit 1
fi

systemctl restart tetrus