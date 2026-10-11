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


class TransferService:
    def __init__(self):
        self._pending = {}
        self._lock = Lock()

    def prepare(self, user_id, account, amount, recipient):
        if not account:
            return {"allowed": False, "reason": "Cuenta inexistente"}

        recipient = str(recipient).strip()

        if not recipient or len(recipient) > 64:
            return {"allowed": False, "reason": "Destinatario inválido"}

        decision = authorize_transfer(
            authenticated_user=user_id,
            account_owner=account["user_id"],
            instruction_source="user",
            confirmed=True,
            amount=str(amount),
            account_status=account["status"],
        )

        if not decision.allowed:
            return {"allowed": False, "reason": decision.reason}

        normalized_amount = str(Decimal(str(amount)))
        operation_id = token_urlsafe(32)

        with self._lock:
            self._pending[operation_id] = {
                "user_id": user_id,
                "amount": normalized_amount,
                "recipient": recipient,
                "expires_at": monotonic() + 120,
            }

        return {
            "allowed": True,
            "operation_id": operation_id,
            "amount": normalized_amount,
            "recipient": recipient,
            "expires_in_seconds": 120,
            "status": "PENDING_CONFIRMATION",
        }

    def cancel(self, user_id, operation_id):
        with self._lock:
            pending = self._pending.get(operation_id)

            if pending is None:
                return {
                    "allowed": False,
                    "reason": "Operación inexistente o ya utilizada",
                }

            if pending["user_id"] != user_id:
                return {
                    "allowed": False,
                    "reason": "La operación pertenece a otro usuario",
                }

            if monotonic() > pending["expires_at"]:
                del self._pending[operation_id]
                return {"allowed": False, "reason": "Operación vencida"}

            del self._pending[operation_id]

            return {
                "allowed": True,
                "status": "CANCELLED",
                "message": "Operación cancelada y revocada en el servidor.",
            }

    def confirm(self, user_id, account, operation_id):
        with self._lock:
            pending = self._pending.get(operation_id)

            if pending is None:
                return {
                    "allowed": False,
                    "reason": "Operación inexistente o ya utilizada",
                }

            if pending["user_id"] != user_id:
                return {
                    "allowed": False,
                    "reason": "La operación pertenece a otro usuario",
                }

            if monotonic() > pending["expires_at"]:
                del self._pending[operation_id]
                return {"allowed": False, "reason": "Operación vencida"}

            if not account:
                return {"allowed": False, "reason": "Cuenta inexistente"}

            decision = authorize_transfer(
                authenticated_user=user_id,
                account_owner=account["user_id"],
                instruction_source="user",
                confirmed=True,
                amount=pending["amount"],
                account_status=account["status"],
            )

            if not decision.allowed:
                return {"allowed": False, "reason": decision.reason}

            del self._pending[operation_id]

            return {
                "allowed": True,
                "status": "SIMULATED",
                "amount": pending["amount"],
                "recipient": pending["recipient"],
                "message": (
                    "Transferencia ficticia autorizada. "
                    "No se modificó ningún saldo."
                ),
            }
