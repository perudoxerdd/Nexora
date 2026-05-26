import os
import asyncio
import unittest
from unittest.mock import patch

os.environ.setdefault("TOKEN_BOT", "123:test")
os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("API_BASE", "http://127.0.0.1:8080")


class UtilsHttpTest(unittest.TestCase):
    def test_api_url_normalizes_paths(self):
        from comandos import utils

        with patch.object(utils, "API_BASE", "https://example.test"):
            self.assertEqual(utils.api_url("/tg_info"), "https://example.test/tg_info")
            self.assertEqual(utils.api_url("tg_info"), "https://example.test/tg_info")

    def test_fetch_api_json_handles_missing_api_base(self):
        from comandos import utils

        with patch.object(utils, "API_BASE", ""):
            status, data = utils.fetch_api_json("/tg_info")

        self.assertEqual(status, 500)
        self.assertEqual(data["status"], "error")
        self.assertIn("API_BASE", data["message"])

    def test_fetch_api_json_delegates_to_common_fetcher(self):
        from comandos import utils

        with patch.object(utils, "API_BASE", "https://example.test"):
            with patch.object(utils, "_fetch_json", return_value=(200, {"status": "ok"})) as fetch_json:
                status, data = utils.fetch_api_json("/tg_info", timeout=7, method="POST", payload={"a": 1})

        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")
        fetch_json.assert_called_once_with(
            "https://example.test/tg_info",
            timeout=7,
            method="POST",
            payload={"a": 1},
        )

    def test_register_uses_shared_api_base(self):
        from comandos import register
        from comandos import utils

        self.assertEqual(register.API_BASE, utils.API_BASE)

    def test_fetch_api_json_async_delegates_to_sync_helper(self):
        from comandos import utils

        async def run_check():
            with patch.object(utils, "fetch_api_json", return_value=(200, {"status": "ok"})) as fetch_json:
                status, data = await utils.fetch_api_json_async("/bot_catalog", timeout=3)
            self.assertEqual(status, 200)
            self.assertEqual(data["status"], "ok")
            fetch_json.assert_called_once_with(
                "/bot_catalog",
                timeout=3,
                method="GET",
                payload=None,
            )

        asyncio.run(run_check())

    def test_configured_admin_ids_uses_nexora_fallbacks(self):
        from comandos import utils

        self.assertEqual(utils.configured_admin_ids("7, 8  bad"), {7, 8})

        with patch.dict(os.environ, {"NEXORA_ADMIN_ID": "7454664711"}, clear=False):
            self.assertIn(7454664711, utils.configured_admin_ids())

    def test_is_admin_id_accepts_string_ids(self):
        from comandos import utils

        with patch.object(utils, "configured_admin_ids", return_value={7454664711}):
            self.assertTrue(utils.is_admin_id("7454664711"))
            self.assertFalse(utils.is_admin_id("abc"))

    def test_default_asset_url_uses_api_base(self):
        from comandos import utils

        with patch.object(utils, "API_BASE", "https://example.test"):
            self.assertEqual(
                utils.default_asset_url("ft start.png"),
                "https://example.test/assets/default/ft%20start.png",
            )

    def test_api_error_text_distinguishes_missing_user(self):
        from comandos.bot_errors import api_error_text

        text = api_error_text("operar comando admin", 404, {"message": "Usuario no encontrado"})

        self.assertIn("Usuario no encontrado en la base", text)
        self.assertIn("/register", text)
        self.assertNotIn("ruta no existe", text)


if __name__ == "__main__":
    unittest.main()
