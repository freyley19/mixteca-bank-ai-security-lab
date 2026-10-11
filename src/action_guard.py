"""
LAB 05 — Action Guard
Mixteca Bank / XI Simposio de Software Libre
Author: @freyley.leyva

Simulador educativo: no realiza transferencias reales.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class ActionDecision:
    allowed: bool
    reason: str


def authorize_transfer(
    authenticated_user: str,
    account_owner: str,
    instruction_source: str,
    confirmed: bool,
    amount: str,
    account_status: str = "RESTRINGIDA",
) -> ActionDecision:
    """Evalúa una operación ficticia mediante reglas independientes de la IA."""

    if instruction_source != "user":
        return ActionDecision(
            False,
            "DENIED: los documentos y herramientas no pueden ordenar transferencias",
        )

    if authenticated_user != account_owner:
        return ActionDecision(
            False,
            "DENIED: el usuario no es propietario de la cuenta",
        )

    if account_status != "ACTIVA":
        return ActionDecision(
            False,
            "DENIED: la cuenta no permite transferencias",
        )

    if confirmed is not True:
        return ActionDecision(
            False,
            "DENIED: falta confirmación explícita",
        )

    try:
        value = Decimal(amount)
    except (InvalidOperation, TypeError, ValueError):
        return ActionDecision(False, "DENIED: importe inválido")

    if not value.is_finite() or not Decimal("0") < value <= Decimal("10000"):
        return ActionDecision(
            False,
            "DENIED: importe fuera del rango permitido",
        )

    return ActionDecision(True, "ALLOWED: operación ficticia autorizada")
