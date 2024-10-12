#!/bin/bash

if ! git pull; then
  echo "Failed to pull from git"
  exit 1
fi

if ! pip install -r requirements.txt; then
  echo "Failed to install requirements"
  exit 1
fi

# reload pm2 process that has been started with
# pm2 start fastapi --name "tetrus"
if ! pm2 reload tetrus; then 
  echo "Failed to reload pm2 process"
  echo "Maybe you need to run 'pm2 start fastapi --name \"tetrus\"' first"
  exit 1
fi