# Author: @freyley.leyva
# Mixteca Bank / UTM — comandos reproducibles del laboratorio
.DEFAULT_GOAL := help
SHELL := /bin/sh
COMPOSE ?= docker compose
SERVICE ?= app
PYTHON ?= python3

.PHONY: help up down restart rebuild ps logs health check syntax json test-attack status checkpoint

help: ## Muestra los comandos disponibles
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Inicia los servicios
	$(COMPOSE) up -d

down: ## Detiene los servicios (sin borrar volúmenes)
	$(COMPOSE) down

restart: ## Reinicia la aplicación
	$(COMPOSE) restart $(SERVICE)

rebuild: ## Reconstruye la imagen y recrea la aplicación
	$(COMPOSE) up -d --build $(SERVICE)

ps: ## Muestra el estado de los contenedores
	$(COMPOSE) ps

logs: ## Sigue los logs de la aplicación
	$(COMPOSE) logs -f --tail=100 $(SERVICE)

health: ## Comprueba la API local
	@curl -fsS http://localhost:8000/health || { echo '\nComprueba el puerto publicado en docker-compose.yml'; exit 1; }

syntax: ## Comprueba sintaxis Python sin importar dependencias
	$(PYTHON) -m py_compile src/app.py src/vector_store.py

json: ## Valida los documentos JSON del laboratorio
	$(PYTHON) -m json.tool data/bank_data.json >/dev/null
	$(PYTHON) -m json.tool data/official_products.json >/dev/null
	@echo 'JSON válido'

check: syntax json ## Ejecuta verificaciones locales rápidas
	@echo 'Verificaciones locales completadas'

test-attack: ## Consulta en Hardened una variante de beneficios (requiere API en puerto 8000)
	@curl -fsS -X POST http://localhost:8000/chat -H 'Content-Type: application/json' \
	  -d '{"user_id":"CLI-001","mode":"hardened","query":"¿Qué ventajas ofrece la Tarjeta Mixteca Oro?"}'
	@printf '\n'

status: ## Revisa cambios antes de preparar el commit
	@git status --short
	@echo 'ATENCIÓN: no incluir data/bank_data.json contaminado en un commit de defensa.'

checkpoint: check status ## Valida el laboratorio y revisa el árbol Git (no crea commit)

# LAB 04: pruebas de autenticación y autorización
# Author: @freyley.leyva

API_URL ?= http://localhost:8000
TOKEN_CLI001 ?=
TOKEN_CLI002 ?=

.PHONY: test-no-auth test-bad-token test-auth test-bola test-security

test-no-auth:
	@status=$$(curl -sS -o /dev/null -w '%{http_code}' \
		-X POST $(API_URL)/chat \
		-H 'Content-Type: application/json' \
		-d '{"user_id":"CLI-001","mode":"hardened","query":"¿Cuál es el saldo de mi cuenta?"}'); \
	test "$$status" = "401" && echo "PASS: sin token -> 401" || { echo "FAIL: esperado 401, recibido $$status"; exit 1; }

test-bad-token:
	@status=$$(curl -sS -o /dev/null -w '%{http_code}' \
		-X POST $(API_URL)/chat \
		-H 'Content-Type: application/json' \
		-H 'Authorization: Bearer token-invalido-lab04' \
		-d '{"user_id":"CLI-001","mode":"hardened","query":"¿Cuál es el saldo de mi cuenta?"}'); \
	test "$$status" = "401" && echo "PASS: token inválido -> 401" || { echo "FAIL: esperado 401, recibido $$status"; exit 1; }

test-auth:
	@test -n "$(TOKEN_CLI001)" || { echo "ERROR: configura TOKEN_CLI001"; exit 1; }
	@status=$$(curl -sS -o /dev/null -w '%{http_code}' \
		-X POST $(API_URL)/chat \
		-H 'Content-Type: application/json' \
		-H 'Authorization: Bearer $(TOKEN_CLI001)' \
		-d '{"user_id":"CLI-001","mode":"hardened","query":"Beneficios oficiales de la Tarjeta Mixteca Oro"}'); \
	test "$$status" = "200" && echo "PASS: acceso autorizado -> 200" || { echo "FAIL: esperado 200, recibido $$status"; exit 1; }

test-bola:
	@test -n "$(TOKEN_CLI001)" || { echo "ERROR: configura TOKEN_CLI001"; exit 1; }
	@status=$$(curl -sS -o /dev/null -w '%{http_code}' \
		-X POST $(API_URL)/chat \
		-H 'Content-Type: application/json' \
		-H 'Authorization: Bearer $(TOKEN_CLI001)' \
		-d '{"user_id":"CLI-002","mode":"hardened","query":"¿Cuál es el saldo de mi cuenta?"}'); \
	test "$$status" = "403" && echo "PASS: acceso cruzado bloqueado -> 403" || { echo "FAIL: esperado 403, recibido $$status"; exit 1; }

test-security: test-no-auth test-bad-token test-auth test-bola test-auth-cli002 test-bola-reverse
	@echo "LAB 04: seis pruebas HTTP superadas"

# LAB 04: pruebas adicionales de autorización
# Author: @freyley.leyva

.PHONY: test-auth-cli002 test-bola-reverse

test-auth-cli002:
	@test -n "$(TOKEN_CLI002)" || { echo "ERROR: configura TOKEN_CLI002"; exit 1; }
	@status=$$(curl -sS -o /dev/null -w '%{http_code}' \
		-X POST $(API_URL)/chat \
		-H 'Content-Type: application/json' \
		-H 'Authorization: Bearer $(TOKEN_CLI002)' \
		-d '{"user_id":"CLI-002","mode":"hardened","query":"Beneficios oficiales de la Tarjeta Mixteca Oro"}'); \
	test "$$status" = "200" && echo "PASS: CLI-002 autorizado -> 200" || { echo "FAIL: esperado 200, recibido $$status"; exit 1; }

test-bola-reverse:
	@test -n "$(TOKEN_CLI002)" || { echo "ERROR: configura TOKEN_CLI002"; exit 1; }
	@status=$$(curl -sS -o /dev/null -w '%{http_code}' \
		-X POST $(API_URL)/chat \
		-H 'Content-Type: application/json' \
		-H 'Authorization: Bearer $(TOKEN_CLI002)' \
		-d '{"user_id":"CLI-001","mode":"hardened","query":"¿Cuál es el saldo de mi cuenta?"}'); \
	test "$$status" = "403" && echo "PASS: acceso cruzado inverso bloqueado -> 403" || { echo "FAIL: esperado 403, recibido $$status"; exit 1; }