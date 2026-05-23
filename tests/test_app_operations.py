import os
import time
import unittest

os.environ.setdefault("TOKEN_BOT", "123:test")
os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("API_BASE", "http://127.0.0.1:8080")
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")
os.environ.setdefault("PANEL_PASSWORD", "test-panel-password")


class AppOperationsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import app

        cls.app_module = app
        cls.client = app.app.test_client()
        cls.headers = {"X-Internal-Api-Key": app.INTERNAL_API_KEY}
        cls.user_prefix = str(time.time_ns())[-8:]

    def user_id(self, suffix: str) -> str:
        return f"91{self.user_prefix}{suffix}"

    def register_user(self, user_id: str):
        response = self.client.get(f"/register?ID_TG={user_id}", headers=self.headers)
        self.assertIn(response.status_code, {200, 423})
        return response

    def test_credit_endpoint_updates_user_balance(self):
        user_id = self.user_id("01")
        self.register_user(user_id)

        response = self.client.post(
            "/cred",
            json={"ID_TG": user_id, "operacion": "sumar", "cantidad": 7},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["CREDITOS"], 12)

    def test_compras_id_returns_recorded_purchase(self):
        user_id = self.user_id("02")
        self.register_user(user_id)
        purchase_id = self.app_module.record_purchase_event(user_id, "seller-test", "30 DIAS")

        response = self.client.get(f"/compras_id?ID_TG={user_id}", headers=self.headers)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(row["ID"] == purchase_id for row in data["data"]))

    def test_key_generate_and_redeem_flow(self):
        user_id = self.user_id("03")
        self.register_user(user_id)

        generated = self.client.post(
            "/keys/generate",
            json={"tipo": "creditos", "cantidad": 3, "usos": 1, "total": 1, "creador_id": 1},
            headers=self.headers,
        )
        self.assertEqual(generated.status_code, 200)
        key = generated.get_json()["data"]["keys"][0]

        redeemed = self.client.post(
            "/keys/redeem",
            json={"key": key, "ID_TG": user_id},
            headers=self.headers,
        )

        self.assertEqual(redeemed.status_code, 200)
        payload = redeemed.get_json()["data"]
        self.assertEqual(payload["tipo"], "creditos")
        self.assertEqual(payload["cantidad"], 3)

    def test_internal_admin_user_action_bans_and_unbans(self):
        user_id = self.user_id("04")
        self.register_user(user_id)

        banned = self.client.post(
            "/internal/admin/user-action",
            json={"ID_TG": user_id, "action": "ban"},
            headers=self.headers,
        )
        self.assertEqual(banned.status_code, 200)
        self.assertEqual(banned.get_json()["estado"], "BANEADO")

        unbanned = self.client.post(
            "/internal/admin/user-action",
            json={"ID_TG": user_id, "action": "unban"},
            headers=self.headers,
        )
        self.assertEqual(unbanned.status_code, 200)
        self.assertEqual(unbanned.get_json()["estado"], "ACTIVO")


if __name__ == "__main__":
    unittest.main()
