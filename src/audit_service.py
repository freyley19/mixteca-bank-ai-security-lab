"""
LAB 06 — Auditoría estructurada de seguridad.
Mixteca Bank · XI Simposio 2026
Author: @freyley.leyva

Registra metadatos mínimos; nunca tokens ni payloads completos.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4


ALLOWED_ACTIONS = {
    "transfer.prepare",
    "transfer.confirm",
    "transfer.cancel",
}

ALLOWED_OUTCOMES = {"ALLOW", "DENY"}

ALLOWED_REASONS = {
    "AUTHORIZED",
    "INVALID_ACCOUNT",
    "INVALID_RECIPIENT",
    "POLICY_DENIED",
    "OPERATION_NOT_FOUND",
    "OPERATION_WRONG_OWNER",
    "OPERATION_EXPIRED",
}


class AuditStorageError(Exception):
    """No fue posible persistir el evento de auditoría."""


class AuditService:
    def __init__(self, path="data/audit_events.jsonl"):
        self.path = Path(path)
        self._lock = Lock()

    def record(self, *, action, outcome, reason_code, actor_id):
        if action not in ALLOWED_ACTIONS:
            raise ValueError("Acción de auditoría inválida")

        if outcome not in ALLOWED_OUTCOMES:
            raise ValueError("Resultado de auditoría inválido")

        if reason_code not in ALLOWED_REASONS:
            raise ValueError("Código de motivo inválido")

        if not isinstance(actor_id, str) or not actor_id.startswith("CLI-"):
            raise ValueError("Identificador de actor inválido")

        event = {
            "event_id": uuid4().hex,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "outcome": outcome,
            "reason_code": reason_code,
            "actor_id": actor_id,
        }

        serialized = json.dumps(event, ensure_ascii=False)

        with self._lock:
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)

                with self.path.open("a", encoding="utf-8") as file:
                    file.write(serialized + "\n")
                    file.flush()
                    os.fsync(file.fileno())
            except OSError as exc:
                raise AuditStorageError(
                    "No se pudo persistir el evento"
                ) from exc

        return event
