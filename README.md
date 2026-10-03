# Mixteca Bank / UTM Bank — AI Security Lab

**Autor:** @freyley.leyva  
**Metodología:** BREAK → DEFEND → PROVE

Laboratorio educativo local para explorar seguridad de aplicaciones con IA usando FastAPI, Ollama, ChromaDB y SQLite. Todos los nombres, cuentas, saldos, reglas y documentos del laboratorio son ficticios.

## Requisitos
- Docker Desktop
- Ollama

## Modelos
```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

## Arranque
```bash
docker compose up --build
```

- Chat: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Nota
El modo vulnerable contiene fallas intencionales para fines educativos. No reutilizar estos patrones en producción.
