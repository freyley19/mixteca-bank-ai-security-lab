"""LAB 06 — Auditoría de seguridad de Mixteca Bank.

Author: @freyley.leyva
"""

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from audit_service import AuditService, AuditStorageError
from transfer_service import TransferService


ALEX = {"user_id": "CLI-001", "status": "ACTIVA"}


class FailingAudit:
    def record(self, **kwargs):
        raise AuditStorageError("FALLO_INTERNO_SIMULADO")


class TestLab06Audit(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "audit.jsonl"
        self.service = TransferService(
            audit=AuditService(self.path)
        )

    def tearDown(self):
        self.temp.cleanup()

    def events(self):
        return [
            json.loads(line)
            for line in self.path.read_text().splitlines()
        ]

    def test_01_authorized_prepare_is_audited(self):
        result = self.service.prepare(
            "CLI-001", ALEX, "100", "DEMO"
        )
        self.assertTrue(result["allowed"])

        event = self.events()[0]
        self.assertEqual(event["action"], "transfer.prepare")
        self.assertEqual(event["outcome"], "ALLOW")
        self.assertEqual(event["reason_code"], "AUTHORIZED")

    def test_02_cross_user_cancel_is_denied_and_audited(self):
        prepared = self.service.prepare(
            "CLI-001", ALEX, "100", "DEMO"
        )
        operation_id = prepared["operation_id"]

        result = self.service.cancel("CLI-002", operation_id)

        self.assertFalse(result["allowed"])
        self.assertEqual(
            self.events()[-1]["reason_code"],
            "OPERATION_WRONG_OWNER",
        )
        self.assertIn(operation_id, self.service._pending)

    def test_03_cancelled_operation_cannot_be_reused(self):
        prepared = self.service.prepare(
            "CLI-001", ALEX, "100", "DEMO"
        )
        operation_id = prepared["operation_id"]

        cancelled = self.service.cancel("CLI-001", operation_id)
        replay = self.service.confirm(
            "CLI-001", ALEX, operation_id
        )

        self.assertEqual(cancelled["status"], "CANCELLED")
        self.assertFalse(replay["allowed"])
        self.assertEqual(
            self.events()[-1]["reason_code"],
            "OPERATION_NOT_FOUND",
        )

    def test_04_sensitive_information_is_not_logged(self):
        prepared = self.service.prepare(
            "CLI-001", ALEX, "100", "DESTINATARIO-SECRETO"
        )

        contents = self.path.read_text()

        self.assertNotIn(
            prepared["operation_id"], contents
        )
        self.assertNotIn(
            "DESTINATARIO-SECRETO", contents
        )
        self.assertNotIn("lab-token-", contents)

    def test_05_audit_failure_preserves_pending_operation(self):
        prepared = self.service.prepare(
            "CLI-001", ALEX, "100", "DEMO"
        )
        operation_id = prepared["operation_id"]

        self.service._audit = FailingAudit()

        with self.assertRaises(AuditStorageError):
            self.service.confirm(
                "CLI-001", ALEX, operation_id
            )

        self.assertIn(operation_id, self.service._pending)

        with self.assertRaises(AuditStorageError):
            self.service.cancel("CLI-001", operation_id)

        self.assertIn(operation_id, self.service._pending)

    def test_06_audit_storage_failure_is_wrapped(self):
        bad_path = Path(self.temp.name) / "as-directory"
        bad_path.mkdir()

        audit = AuditService(bad_path)

        with self.assertRaises(AuditStorageError):
            audit.record(
                action="transfer.prepare",
                outcome="ALLOW",
                reason_code="AUTHORIZED",
                actor_id="CLI-001",
            )

    def test_07_http_returns_503_without_internal_details(self):
        import httpx
        import app

        service = app.transfer_service
        original_audit = service._audit
        pending_before = set(service._pending)

        async def check():
            transport = httpx.ASGITransport(
                app=app.app,
                raise_app_exceptions=False,
            )

            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.post(
                    "/lab05/transfers/prepare",
                    headers={
                        "Authorization":
                        "Bearer lab-token-alex-001"
                    },
                    json={
                        "amount": "100",
                        "recipient": "DEMO",
                    },
                )

        try:
            service._audit = FailingAudit()
            response = asyncio.run(check())

            self.assertEqual(response.status_code, 503)
            self.assertNotIn(
                "FALLO_INTERNO_SIMULADO", response.text
            )
            self.assertEqual(
                set(service._pending), pending_before
            )
        finally:
            service._audit = original_audit


if __name__ == "__main__":
    unittest.main()
