import os
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


if __name__ == "__main__":
    unittest.main()
