"""
LAB 05 — Servicio de transferencias simuladas.
Mixteca Bank · XI Simposio 2026
Author: @freyley.leyva

No ejecuta transferencias ni modifica saldos.
"""

from decimal import Decimal
from threading import Lock
from time import monotonic
from secrets import token_urlsafe

from action_guard import authorize_transfer
from transfer_audit import audit_decision


class TransferService:
    def __init__(self, audit=None):
        self._pending = {}
        self._lock = Lock()
        self._audit = audit

    def _record(self, action, user_id, result):
        audit_decision(
            self._audit,
            action=action,
            user_id=user_id,
            result=result,
        )

    def prepare(self, user_id, account, amount, recipient):
        action = "transfer.prepare"

        if not account:
            result = {"allowed": False, "reason": "Cuenta inexistente"}
            self._record(action, user_id, result)
            return result

        recipient = str(recipient).strip()

        if not recipient or len(recipient) > 64:
            result = {"allowed": False, "reason": "Destinatario inválido"}
            self._record(action, user_id, result)
            return result

        decision = authorize_transfer(
            authenticated_user=user_id,
            account_owner=account["user_id"],
            instruction_source="user",
            confirmed=True,
            amount=str(amount),
            account_status=account["status"],
        )

        if not decision.allowed:
            result = {"allowed": False, "reason": decision.reason}
            self._record(action, user_id, result)
            return result

        normalized_amount = str(Decimal(str(amount)))
        operation_id = token_urlsafe(32)

        result = {
            "allowed": True,
            "operation_id": operation_id,
            "amount": normalized_amount,
            "recipient": recipient,
            "expires_in_seconds": 120,
            "status": "PENDING_CONFIRMATION",
        }

        with self._lock:
            self._record(action, user_id, result)
            self._pending[operation_id] = {
                "user_id": user_id,
                "amount": normalized_amount,
                "recipient": recipient,
                "expires_at": monotonic() + 120,
            }

        return result

    def cancel(self, user_id, operation_id):
        action = "transfer.cancel"

        with self._lock:
            pending = self._pending.get(operation_id)

            if pending is None:
                result = {
                    "allowed": False,
                    "reason": "Operación inexistente o ya utilizada",
                }
                self._record(action, user_id, result)
                return result

            if pending["user_id"] != user_id:
                result = {
                    "allowed": False,
                    "reason": "La operación pertenece a otro usuario",
                }
                self._record(action, user_id, result)
                return result

            if monotonic() > pending["expires_at"]:
                result = {"allowed": False, "reason": "Operación vencida"}
                self._record(action, user_id, result)
                del self._pending[operation_id]
                return result

            result = {
                "allowed": True,
                "status": "CANCELLED",
                "message": "Operación cancelada y revocada en el servidor.",
            }

            self._record(action, user_id, result)
            del self._pending[operation_id]
            return result

    def confirm(self, user_id, account, operation_id):
        action = "transfer.confirm"

        with self._lock:
            pending = self._pending.get(operation_id)

            if pending is None:
                result = {
                    "allowed": False,
                    "reason": "Operación inexistente o ya utilizada",
                }
                self._record(action, user_id, result)
                return result

            if pending["user_id"] != user_id:
                result = {
                    "allowed": False,
                    "reason": "La operación pertenece a otro usuario",
                }
                self._record(action, user_id, result)
                return result

            if monotonic() > pending["expires_at"]:
                result = {"allowed": False, "reason": "Operación vencida"}
                self._record(action, user_id, result)
                del self._pending[operation_id]
                return result

            if not account:
                result = {"allowed": False, "reason": "Cuenta inexistente"}
                self._record(action, user_id, result)
                return result

            decision = authorize_transfer(
                authenticated_user=user_id,
                account_owner=account["user_id"],
                instruction_source="user",
                confirmed=True,
                amount=pending["amount"],
                account_status=account["status"],
            )

            if not decision.allowed:
                result = {"allowed": False, "reason": decision.reason}
                self._record(action, user_id, result)
                return result

            result = {
                "allowed": True,
                "status": "SIMULATED",
                "amount": pending["amount"],
                "recipient": pending["recipient"],
                "message": (
                    "Transferencia ficticia autorizada. "
                    "No se modificó ningún saldo."
                ),
            }

            self._record(action, user_id, result)
            del self._pending[operation_id]
            return result
