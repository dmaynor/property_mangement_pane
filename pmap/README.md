# PMAP AppFolio Read-Only Prototype

## Quickstart
```bash
# Build and run the services in the background
docker-compose up --build -d

# Check the health of the API
curl http://127.0.0.1:8000/health

# Trigger a pull from the mock AppFolio API
curl -X POST http://127.0.0.1:8000/connectors/appfolio/pull
```

## Running Tests
```bash
# Run the tests
docker-compose exec web python -m pytest -q pmap/
```

## Overview
This project is a prototype for a read-only connector for AppFolio, as part of the Property Management Automation Platform (PMAP). It includes:
- A FastAPI application that exposes the connector's operations.
- A mock AppFolio API server for testing.
- A PostgreSQL database for storing normalized data.
- A containerized environment using Docker and Docker Compose.
