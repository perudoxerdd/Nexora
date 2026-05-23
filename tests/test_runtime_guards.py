import contextlib
import importlib
import io
import os
import sys
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("TOKEN_BOT", "123:test")
os.environ.setdefault("ADMIN_ID", "1")
os.environ.setdefault("API_BASE", "http://127.0.0.1:8080")


class DummyApplication:
    def __init__(self):
        self.bot_data = {}


class DummyContext:
    def __init__(self):
        self.application = DummyApplication()


class RuntimeGuardTest(unittest.TestCase):
    def test_main_antispam_cache_reuses_recent_value(self):
        sys.modules.pop("main", None)
        with contextlib.redirect_stdout(io.StringIO()):
            main = importlib.import_module("main")

        main._antispam_cache.clear()
        with patch.object(main, "_fetch_json", return_value=(200, {"data": {"ANTISPAM": "42"}})) as fetch_json:
            first = main._get_antispam_seconds(123)
            second = main._get_antispam_seconds(123)

        self.assertEqual(first, 42)
        self.assertEqual(second, 42)
        self.assertEqual(fetch_json.call_count, 1)

    def test_main_antispam_cache_expires(self):
        sys.modules.pop("main", None)
        with contextlib.redirect_stdout(io.StringIO()):
            main = importlib.import_module("main")

        main._antispam_cache.clear()
        main._antispam_cache[123] = (time.monotonic() - main.ANTISPAM_CACHE_TTL - 1, 9)
        with patch.object(main, "_fetch_json", return_value=(200, {"data": {"ANTISPAM": "31"}})) as fetch_json:
            value = main._get_antispam_seconds(123)

        self.assertEqual(value, 31)
        self.assertEqual(fetch_json.call_count, 1)

    def test_manual_catalog_blocks_insufficient_plan(self):
        from comandos import manual_catalog

        required_plan = manual_catalog._normalize_plan("premium")
        current_plan = manual_catalog._user_plan({"PLAN": "BASICO"})

        self.assertLess(manual_catalog.PLAN_LEVELS[current_plan], manual_catalog.PLAN_LEVELS[required_plan])
        self.assertIn("requiere plan Premium", manual_catalog._plan_block_message("demo", required_plan, current_plan))

    def test_manual_catalog_privileged_user_bypasses_plan_and_cooldown(self):
        from comandos import manual_catalog

        info = {"ROL_TG": "FUNDADOR", "ANTISPAM": 999}
        context = DummyContext()

        self.assertTrue(manual_catalog._is_privileged_user(info))
        self.assertIsNone(manual_catalog._check_request_cooldown(context, 999, info))
        self.assertEqual(context.application.bot_data, {})

    def test_manual_catalog_cooldown_blocks_second_call(self):
        from comandos import manual_catalog

        context = DummyContext()
        info = {"ROL_TG": "FREE", "ANTISPAM": 60}

        first = manual_catalog._check_request_cooldown(context, 123, info)
        second = manual_catalog._check_request_cooldown(context, 123, info)

        self.assertIsNone(first)
        self.assertIsNotNone(second)
        self.assertIn("anti-spam", second)


if __name__ == "__main__":
    unittest.main()
