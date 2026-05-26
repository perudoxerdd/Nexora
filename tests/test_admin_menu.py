import unittest

from comandos import helpadmin


class AdminMenuTests(unittest.TestCase):
    def test_home_mentions_new_and_legacy_commands(self):
        text = helpadmin._render("home", "ADMIN")
        self.assertIn("/admin", text)
        self.assertIn("/helpadmin", text)
        self.assertIn("/cmdsadmin", text)

    def test_section_renders_expected_commands(self):
        text = helpadmin._render("diag", "ADMIN")
        self.assertIn("/status", text)
        self.assertIn("/errores", text)

    def test_unknown_section_falls_back_to_home(self):
        text = helpadmin._render("nope", "ADMIN")
        self.assertIn("MENU ADMIN", text)


if __name__ == "__main__":
    unittest.main()
