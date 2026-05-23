import os
import re
import unittest

os.environ.setdefault("TOKEN_BOT", "123:test")
os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("API_BASE", "http://127.0.0.1:8080")
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")
os.environ.setdefault("PANEL_PASSWORD", "test-panel-password")


class SecurityHardeningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import app

        cls.app_module = app
        cls.client = app.app.test_client()

    def test_admin_post_requires_csrf(self):
        response = self.client.post(
            "/admin/login",
            data={"username": "admin", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 400)

    def test_admin_login_page_provides_csrf_token(self):
        response = self.client.get("/admin/login")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="csrf_token"', body)

    def test_admin_post_accepts_valid_csrf(self):
        login_page = self.client.get("/admin/login").get_data(as_text=True)
        match = re.search(r'name="csrf_token" value="([^"]+)"', login_page)
        self.assertIsNotNone(match)

        response = self.client.post(
            "/admin/login",
            data={
                "username": "admin",
                "password": "wrong",
                "csrf_token": match.group(1),
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_internal_access_requires_configured_key(self):
        response = self.client.get("/tg_info?ID_TG=1")

        self.assertEqual(response.status_code, 403)

    def test_internal_access_accepts_configured_key(self):
        response = self.client.get(
            "/tg_info?ID_TG=missing",
            headers={"X-Internal-Api-Key": "test-internal-key"},
        )

        self.assertNotEqual(response.status_code, 403)

    def test_request_token_value_accepts_bearer_and_api_token_headers(self):
        with self.app_module.app.test_request_context(
            "/info_web",
            headers={"Authorization": "Bearer bearer-token"},
        ):
            self.assertEqual(self.app_module.request_token_value(), "bearer-token")

        with self.app_module.app.test_request_context(
            "/info_web",
            headers={"X-Api-Token": "header-token"},
        ):
            self.assertEqual(self.app_module.request_token_value(), "header-token")


if __name__ == "__main__":
    unittest.main()
