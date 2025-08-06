#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Error: .env file not found."
  echo "Please create a .env file based on .env.example and fill in your API keys and master key."
  exit 1
fi

echo "Starting Chimera Overlord services..."

docker-compose up --build -d

if [ $? -eq 0 ]; then
  echo "
Chimera Overlord services started successfully in detached mode."
  echo "Access the Mission Control Dashboard at: http://localhost:8501"
  echo "
To stop services, run: docker-compose down"
else
  echo "Error: Failed to start Chimera Overlord services."
  echo "Please check the logs for more details."
fi


