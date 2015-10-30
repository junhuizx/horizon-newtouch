from horizon.test import helpers as test


class ServerTests(test.TestCase):
    # Unit tests for server.
    def test_me(self):
        self.assertTrue(1 + 1 == 2)
