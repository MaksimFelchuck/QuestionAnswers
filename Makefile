.PHONY: help test test-verbose test-coverage build up down logs clean

help: ## Показать справку по командам
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Запустить тесты
	docker-compose run --rm app pytest app/tests/

test-verbose: ## Запустить тесты с подробным выводом
	docker-compose run --rm app pytest app/tests/ -v

test-coverage: ## Запустить тесты с покрытием кода
	docker-compose run --rm app pytest app/tests/ --cov=app --cov-report=html --cov-report=term

build: ## Собрать Docker образ
	docker-compose build

up: ## Запустить приложение (сначала тесты)
	@echo "Running tests first..."
	@make test
	@echo "Tests passed! Starting application..."
	docker-compose up -d

up-only: ## Запустить только приложение без тестов
	docker-compose up -d

down: ## Остановить приложение
	docker-compose down

logs: ## Показать логи
	docker-compose logs -f app

clean: ## Очистить все контейнеры и образы
	docker-compose down -v --rmi all
	docker system prune -f
