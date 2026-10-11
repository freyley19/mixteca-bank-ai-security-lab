"""
LAB 06 — Adaptador de auditoría de transferencias simuladas.
Author: @freyley.leyva
"""

REASON_CODES = {
    "Cuenta inexistente": "INVALID_ACCOUNT",
    "Destinatario inválido": "INVALID_RECIPIENT",
    "Operación inexistente o ya utilizada": "OPERATION_NOT_FOUND",
    "La operación pertenece a otro usuario": "OPERATION_WRONG_OWNER",
    "Operación vencida": "OPERATION_EXPIRED",
}


def audit_decision(audit, *, action, user_id, result):
    if audit is None:
        return

    allowed = result["allowed"]
    reason_code = (
        "AUTHORIZED"
        if allowed
        else REASON_CODES.get(result.get("reason"), "POLICY_DENIED")
    )

    audit.record(
        action=action,
        outcome="ALLOW" if allowed else "DENY",
        reason_code=reason_code,
        actor_id=user_id,
    )
