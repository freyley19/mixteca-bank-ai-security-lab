# LAB 06 — Auditoría de decisiones de seguridad

Autor: @freyley.leyva

Objetivo: registrar y verificar decisiones de seguridad.
## 1. ¿Qué aprenderemos?

En este laboratorio aprenderemos a registrar las decisiones de seguridad de una aplicación con inteligencia artificial.

Al finalizar podrás:

- Distinguir una operación autorizada (ALLOW) de una rechazada (DENY).
- Explicar qué es un registro de auditoría.
- Identificar qué información no debe almacenarse.
- Comprender el principio de seguridad *fail closed*.
- Ejecutar pruebas automatizadas para verificar estos controles.

## 2. Arquitectura del laboratorio

La aplicación utiliza los siguientes componentes:

- **FastAPI:** recibe las solicitudes HTTP.
- **ActionGuard:** comprueba las reglas de autorización.
- **TransferService:** administra operaciones ficticias pendientes.
- **transfer_audit.py:** traduce las decisiones a eventos de auditoría.
- **AuditService:** registra los eventos en un archivo JSONL.

El archivo de auditoría se encuentra en `data/audit_events.jsonl`.

## 3. Primera práctica: verificar la aplicación

Desde una terminal ubicada en la raíz del proyecto, ejecuta:

`docker compose up -d --build`

Después comprueba que el servidor responda:

`curl http://localhost:8000/health`

La respuesta esperada es un objeto JSON con `status` igual a `ok`.

## 4. Segunda práctica: ejecutar las pruebas

Ejecuta el siguiente comando:

`docker compose exec -T app python -m unittest discover -s tests -p 'test_lab06_audit.py' -v`

El resultado esperado es **7 pruebas ejecutadas correctamente**, finalizando con `OK`.

## 5. Preguntas para reflexionar

1. ¿Por qué debemos registrar las operaciones rechazadas?
2. ¿Qué podría ocurrir si guardamos tokens de autenticación?
3. ¿Por qué una aplicación debe impedir una operación cuando falla su auditoría?
4. ¿Qué limitaciones tiene almacenar los registros en un archivo local?
## 6. Tercera práctica: cancelación y prevención de reutilización

Una operación pendiente no debe permanecer disponible después de cancelarse.

**BREAK — ¿Qué podría salir mal?**

Imagina que un usuario cancela una transferencia ficticia, pero conserva su identificador de operación.

¿Qué ocurriría si el servidor permitiera confirmarla después?

**DEFEND — Control implementado**

`TransferService` administra el estado de las operaciones pendientes y evita que una operación cancelada vuelva a utilizarse.

También comprueba que quien solicita la cancelación sea el propietario de la operación.

**PROVE — Demostración**

Ejecuta las pruebas HTTP del LAB 05:

`docker compose exec -T app python -m unittest discover -s tests -p 'test_lab05_cancel_http.py' -v`

Resultado esperado: **3 pruebas satisfactorias**.

Después ejecuta nuevamente las pruebas del LAB 06:

`docker compose exec -T app python -m unittest discover -s tests -p 'test_lab06_audit.py' -v`

Localiza en `tests/test_lab06_audit.py` las pruebas relacionadas con la cancelación y la reutilización de operaciones.

**Pregunta:** ¿Por qué el servidor debe invalidar una operación, aunque el cliente todavía conserve su identificador?

## 7. Cuarta práctica: inspeccionar los eventos de auditoría

El sistema registra decisiones de autorización y rechazo en:

`data/audit_events.jsonl`

Si el archivo contiene eventos, puedes examinar sus últimas líneas desde la raíz del proyecto:

`tail -n 10 data/audit_events.jsonl`

Identifica los siguientes campos:

- `event_id`
- `timestamp`
- `action`
- `outcome`
- `reason_code`
- `actor_id`

Busca eventos con resultado `ALLOW` y `DENY`.

**Pregunta:** ¿Por qué utilizamos códigos controlados como `POLICY_DENIED` en lugar de guardar el texto completo de una solicitud?

## 8. Quinta práctica: fallar de forma segura

**BREAK — Escenario de falla**

Supongamos que el almacenamiento de auditoría deja de estar disponible.

¿Debería continuar una operación si no puede registrarse su decisión de seguridad?

**DEFEND — Control implementado**

En el flujo de transferencias ficticias, el servicio intenta registrar la decisión antes de modificar el estado de la operación pendiente.

Si la auditoría falla, se produce un error controlado y la operación no debe continuar silenciosamente.

**PROVE — Demostración**

Ejecuta:

`docker compose exec -T app python -m unittest discover -s tests -p 'test_lab06_audit.py' -v`

Identifica las pruebas que simulan fallos de almacenamiento y verifican la respuesta HTTP 503.

**Pregunta:** ¿Qué diferencia existe entre una falla controlada y una operación que continúa sin dejar evidencia?

## 9. Límites de seguridad del prototipo

Mixteca Bank es un laboratorio educativo, no una plataforma bancaria de producción.

- Las transferencias son simuladas y no modifican saldos.
- Las operaciones pendientes se mantienen en memoria.
- La auditoría utiliza un archivo JSONL local.
- No existe una transacción atómica entre auditoría y operaciones.
- Una falla de escritura puede dejar un registro parcial.
- El diseño no garantiza coordinación entre varios procesos independientes.

**Reto avanzado:** propone una arquitectura para mantener consistencia entre operaciones y auditoría utilizando una base de datos transaccional.

## 10. Criterios de finalización

- [ ] Ejecuté las siete pruebas del LAB 06.
- [ ] Verifiqué las pruebas HTTP de cancelación del LAB 05.
- [ ] Identifiqué eventos `ALLOW` y `DENY`.
- [ ] Comprendí por qué una operación cancelada no puede reutilizarse.
- [ ] Expliqué el comportamiento *fail closed*.
- [ ] Reconozco las limitaciones del prototipo.

---

**Mixteca Bank — XI Simposio 2026**
**Autor:** @freyley.leyva
