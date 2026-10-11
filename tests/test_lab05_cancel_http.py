"""
LAB 05 — Pruebas HTTP de revocación.
Mixteca Bank · XI Simposio 2026
Author: @freyley.leyva
"""

import json
import unittest
import urllib.error
import urllib.request


BASE = "http://localhost:8000"
ALEX = "lab-token-alex-001"
SAM = "lab-token-sam-002"


def post(path, token, payload):
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


class TestLab05Cancellation(unittest.TestCase):

    def prepare_alex(self):
        status, result = post(
            "/lab05/transfers/prepare",
            ALEX,
            {"amount": "5000", "recipient": "DEST-DEMO-001"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "PENDING_CONFIRMATION")
        return result["operation_id"]

    def test_cancel_blocks_confirmation(self):
        operation_id = self.prepare_alex()

        status, result = post(
            "/lab05/transfers/cancel",
            ALEX,
            {"operation_id": operation_id},
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "CANCELLED")

        status, _ = post(
            "/lab05/transfers/confirm",
            ALEX,
            {"operation_id": operation_id},
        )
        self.assertEqual(status, 403)

    def test_cross_user_cancel_denied(self):
        operation_id = self.prepare_alex()

        status, _ = post(
            "/lab05/transfers/cancel",
            SAM,
            {"operation_id": operation_id},
        )
        self.assertEqual(status, 403)

        # El intento de Sam no debe revocar la operación de Alex.
        status, result = post(
            "/lab05/transfers/cancel",
            ALEX,
            {"operation_id": operation_id},
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "CANCELLED")

    def test_double_cancel_denied(self):
        operation_id = self.prepare_alex()

        status, _ = post(
            "/lab05/transfers/cancel",
            ALEX,
            {"operation_id": operation_id},
        )
        self.assertEqual(status, 200)

        status, _ = post(
            "/lab05/transfers/cancel",
            ALEX,
            {"operation_id": operation_id},
        )
        self.assertEqual(status, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
