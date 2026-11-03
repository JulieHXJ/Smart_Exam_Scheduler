
# Smart Exam Scheduler - Development Commands

SHELL := /bin/bash

PYTHON := .venv/bin/python
COMPOSE := docker compose -f mailpit.compose.yml

.PHONY: help dev api web mailpit stop test install status

.DEFAULT_GOAL := help

# Show available commands
help:
	@echo ""
	@echo "Smart Exam Scheduler"
	@echo "------------------------------"
	@echo "make dev      Start all services"
	@echo "make api      Start FastAPI only"
	@echo "make web      Start React only"
	@echo "make mailpit  Start Mailpit only"
	@echo "make stop     Stop Mailpit"
	@echo "make test     Run backend tests"
	@echo "make install  Install dependencies"
	@echo "make status   Show Mailpit status"
	@echo ""

# Start all services
dev: mailpit
	@echo "Starting FastAPI and React..."
	@$(MAKE) -j2 api web

# Start FastAPI
api:
	cd backend && ../$(PYTHON) -m uvicorn app.main:app --reload --port 8000

# Start React / Vite
web:
	cd frontend && npm run dev

# Start Mailpit in Docker
mailpit:
	$(COMPOSE) up -d

# Stop Mailpit
stop:
	$(COMPOSE) down

# Run backend tests
test:
	cd backend && ../$(PYTHON) -m pytest -v

# Install backend and frontend dependencies
install:
	$(PYTHON) -m pip install -r backend/requirements.txt
	$(PYTHON) -m pip install pytest httpx
	cd frontend && npm ci

# Check Mailpit container
status:
	$(COMPOSE) ps
