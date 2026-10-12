# Preparación del estudiante — Mixteca Bank

**XI Simposio 2026 — UTM**
**Autor:** @freyley.leyva
**Duración del taller:** 3 horas
**Metodología:** BREAK → DEFEND → PROVE

## 1. Bienvenida

En este taller exploraremos cómo se construye y protege una aplicación que integra inteligencia artificial.

Trabajaremos con Mixteca Bank, una aplicación bancaria ficticia que utiliza FastAPI, Docker, Ollama, modelos de lenguaje, recuperación de información y controles de seguridad.

No necesitas ser especialista en inteligencia artificial ni ciberseguridad. Comenzaremos con los fundamentos y avanzaremos mediante ejercicios prácticos.

Si ya tienes experiencia, encontrarás retos adicionales para profundizar.

## 2. Herramientas necesarias

Instala las siguientes herramientas antes del taller:

- **Git:** para descargar y gestionar el código del proyecto.
- **Docker Desktop:** para ejecutar la aplicación en un contenedor.
- **Ollama:** para ejecutar modelos de inteligencia artificial localmente.
- **Navegador web:** Chrome, Firefox, Safari o Edge.
- **Editor de código:** Visual Studio Code u otro de tu preferencia.

No necesitas instalar Python en tu computadora para ejecutar la aplicación: Docker utiliza Python 3.11 dentro del contenedor.

En Linux puedes utilizar Docker Engine con Docker Compose en lugar de Docker Desktop.

## 3. Modelos de inteligencia artificial

Mixteca Bank utiliza dos modelos:

**Qwen 2.5 (1.5B)**

Es el modelo de lenguaje que interpreta preguntas y genera respuestas.

**nomic-embed-text**

Es un modelo de embeddings: convierte textos en representaciones numéricas que permiten buscar información relacionada por significado.

Con Ollama instalado, descarga ambos modelos desde una terminal:

`ollama pull qwen2.5:1.5b`

`ollama pull nomic-embed-text`

Comprueba que están disponibles:

`ollama list`

Los modelos se ejecutan localmente. La descarga inicial requiere conexión a Internet.

## 4. Preparar el proyecto

Abre una terminal y clona el repositorio:

`git clone https://github.com/freyley19/mixteca-bank-ai-security-lab.git`

Entra al directorio:

`cd mixteca-bank-ai-security-lab`

Selecciona la rama utilizada para el taller:

`git switch lab/05-security-hardening`

Confirma la rama activa:

`git branch --show-current`

## 5. Iniciar Mixteca Bank

Asegúrate de que Docker y Ollama estén funcionando.

Desde la raíz del proyecto ejecuta:

`docker compose up -d --build`

La primera ejecución puede tardar varios minutos porque Docker necesita descargar la imagen base e instalar las dependencias.

Comprueba el estado:

`docker compose ps`

Para detener los servicios al terminar:

`docker compose down`

## 6. Verificar que la aplicación funciona

Abre las siguientes direcciones en tu navegador:

- Interfaz del laboratorio: http://localhost:8000
- Documentación interactiva de la API: http://localhost:8000/docs
- Estado de la aplicación: http://localhost:8000/health

En la página de estado deberías encontrar `status` con valor `ok` y el modelo `qwen2.5:1.5b`.

## 7. Checklist previo al taller

- [ ] Tengo Git instalado.
- [ ] Docker funciona correctamente.
- [ ] Ollama está instalado y ejecutándose.
- [ ] Descargué los dos modelos.
- [ ] Cloné el repositorio.
- [ ] Seleccioné la rama indicada.
- [ ] La aplicación inicia sin errores.
- [ ] Puedo abrir la interfaz del laboratorio.
- [ ] Puedo acceder a la documentación de FastAPI.

**Si alguna comprobación falla, conserva el mensaje de error para revisarlo durante la preparación o al inicio del taller.**

## 8. Solución de problemas frecuentes

### Docker no está funcionando

**Síntoma:** aparece un mensaje indicando que no es posible conectarse al servicio Docker.

**Qué hacer:**

1. Abre Docker Desktop.
2. Espera a que el motor de Docker termine de iniciar.
3. Ejecuta `docker info` para comprobar que responde.
4. Intenta nuevamente `docker compose up -d --build`.

En Linux, comprueba que Docker Engine esté iniciado y que tu usuario tenga permisos para utilizarlo.

### El puerto 8000 está ocupado

**Síntoma:** Docker indica que no puede publicar el puerto 8000.

**Qué hacer:**

1. Comprueba si otra aplicación está utilizando el puerto.
2. Detén esa aplicación si es seguro hacerlo.
3. Ejecuta nuevamente `docker compose up -d --build`.

Como alternativa, con ayuda del instructor, puedes cambiar temporalmente el puerto publicado en `docker-compose.yml`.

### Ollama no responde

**Síntoma:** la aplicación inicia, pero no puede comunicarse con el modelo de lenguaje.

**Qué hacer:**

1. Comprueba que Ollama esté abierto y funcionando.
2. Ejecuta `ollama list` para verificar los modelos.
3. Comprueba que Ollama esté escuchando en el puerto 11434.
4. Revisa los mensajes de la aplicación con `docker compose logs --tail=100 app`.

Mixteca Bank utiliza la dirección `host.docker.internal` para conectar el contenedor con Ollama en la computadora anfitriona.

### Faltan modelos

Si `ollama list` no muestra los modelos necesarios, ejecuta:

`ollama pull qwen2.5:1.5b`

`ollama pull nomic-embed-text`

Después intenta nuevamente la actividad.

### La aplicación muestra un error

Consulta los registros del contenedor:

`docker compose logs --tail=100 app`

Si el problema continúa, conserva el mensaje de error y solicita apoyo al instructor.

### Windows: consideraciones especiales

- Utiliza Docker Desktop con el backend WSL 2 habilitado.
- Ejecuta los comandos desde PowerShell o una terminal compatible.
- Verifica que Docker Desktop esté iniciado antes de ejecutar Compose.
- Evita cambiar de terminal o directorio a mitad del laboratorio.

### macOS: consideraciones especiales

- Comprueba que Docker Desktop sea compatible con el procesador de tu Mac.
- Mantén Ollama en ejecución durante el taller.
- Utiliza Terminal o una terminal integrada en tu editor de código.

### Linux: consideraciones especiales

- Docker Engine y el complemento Docker Compose deben estar instalados.
- La configuración de red puede variar según la distribución.
- Comprueba la conectividad entre el contenedor y Ollama antes del taller.

## 9. Verificación de conectividad con Ollama

Antes de comenzar, comprueba que Ollama responda desde tu computadora:

`ollama list`

Después comprueba que Docker pueda comunicarse con Ollama:

`docker compose exec -T app python -c 'import os, urllib.request; print(urllib.request.urlopen(os.environ["OLLAMA_HOST"] + "/api/tags", timeout=10).status)'`

El resultado esperado de la segunda comprobación es `200`.

Esta prueba confirma que el contenedor puede comunicarse con la API HTTP de Ollama, pero no garantiza por sí sola que el modelo genere respuestas correctamente.

Si la conexión falla, revisa que Ollama esté funcionando y que `OLLAMA_HOST` esté configurado correctamente.

## 10. Recomendaciones para el día del taller

- Llega con Docker Desktop y Ollama iniciados.
- Descarga los modelos antes de asistir.
- Mantén suficiente espacio disponible para las imágenes y dependencias.
- No compartas tokens de autenticación ni información personal durante las prácticas.
- Trabaja únicamente con las cuentas y documentos ficticios del laboratorio.
- Conserva tus cambios para poder revisar qué aprendiste.

**Recuerda:** el objetivo no es memorizar comandos. Es comprender cómo funciona la aplicación, identificar riesgos y aprender a introducir controles de seguridad verificables.

---

**Mixteca Bank — XI Simposio 2026**
**Autor:** @freyley.leyva
