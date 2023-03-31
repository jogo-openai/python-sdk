import unittest

from statsig import StatsigServer, StatsigUser, StatsigOptions


class TestLocalMocks(unittest.TestCase):

    def test_local_mode_defaults(self):
        options = StatsigOptions(local_mode=True, disable_diagnostics=True)
        server = StatsigServer()
        server.initialize("secret-key", options)

        user = StatsigUser("123", email="testuser@statsig.com")

        self.assertEqual(
            server.check_gate(user, "any_gate"),
            False
        )

        self.assertEqual(
            server.get_config(user, "any_config").get_value(),
            {}
        )

        self.assertEqual(
            server.get_experiment(user, "any_experiment").get_value(),
            {}
        )

    def test_override_gate(self):
        options = StatsigOptions(local_mode=True, disable_diagnostics=True)
        server = StatsigServer()
        server.initialize("secret-key", options)

        user_one = StatsigUser("123", email="testuser@statsig.com")
        user_two = StatsigUser("456", email="test@statsig.com")

        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            False
        )

        server.override_gate("any_gate", True, "123")

        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            True
        )

        self.assertEqual(
            server.check_gate(user_two, "any_gate"),
            False
        )

        server.override_gate("any_gate", False, "123")
        server.override_gate("any_gate", True, "456")

        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            False
        )

        self.assertEqual(
            server.check_gate(user_two, "any_gate"),
            True
        )

        # Global overrides respect user level overrides first
        server.override_gate("any_gate", True)
        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            False
        )
        self.assertEqual(
            server.check_gate(user_two, "any_gate"),
            True
        )
        self.assertEqual(
            server.check_gate(StatsigUser("4123980"), "any_gate"),
            True
        )

        # remove user override first
        server.remove_gate_override("any_gate", "123")
        # user one should now use global override
        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            True
        )

        # remove global override
        server.remove_gate_override("any_gate")
        # user one should now have no override
        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            False
        )

        # remove all overrides
        server.remove_all_overrides()
        self.assertEqual(
            server.check_gate(user_two, "any_gate"),
            False
        )

        # try removing one that doesn't exist
        server.remove_gate_override("fake_gate_non_existent")

    def test_override_all(self):
        options = StatsigOptions(local_mode=True, disable_diagnostics=True)
        server = StatsigServer()
        server.initialize("secret-key", options)

        user_one = StatsigUser("123", email="testuser@statsig.com")
        user_two = StatsigUser("456", email="test@statsig.com")

        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            False
        )

        self.assertEqual(
            server.check_gate(user_two, "any_gate"),
            False
        )

        server.override_gate("any_gate", True)

        self.assertEqual(
            server.check_gate(user_one, "any_gate"),
            True
        )

        self.assertEqual(
            server.check_gate(user_two, "any_gate"),
            True
        )

        server.override_experiment("my_experiment", {"test": False})

        self.assertEqual(
            server.get_experiment(user_one, "my_experiment").get_value(),
            {"test": False}
        )

        self.assertEqual(
            server.get_experiment(user_two, "my_experiment").get_value(),
            {"test": False}
        )

    def test_override_config(self):
        options = StatsigOptions(local_mode=True, disable_diagnostics=True)
        server = StatsigServer()
        server.initialize("secret-key", options)

        user_one = StatsigUser("123", email="testuser@statsig.com")
        user_two = StatsigUser("456", email="test@statsig.com")

        self.assertEqual(
            server.get_config(user_one, "config").get_value(),
            {}
        )

        self.assertEqual(
            server.get_config(user_two, "config").get_value(),
            {}
        )

        override = {"test": 123}
        server.override_config("config", override, "123")

        self.assertEqual(
            server.get_config(user_one, "config").get_value(),
            override
        )

        self.assertEqual(
            server.get_config(user_two, "config").get_value(),
            {}
        )

        server.override_experiment("config", {}, "123")
        new_override = {"abc": "def"}
        server.override_experiment("config", new_override, "456")

        self.assertEqual(
            server.get_config(user_one, "config").get_value(),
            {}
        )

        self.assertEqual(
            server.get_config(user_two, "config").get_value(),
            new_override
        )

        # Global overrides respect user level overrides first
        new_override_2 = {"123": "ttt"}
        server.override_config("config", new_override_2)

        self.assertEqual(
            server.get_config(user_one, "config").get_value(),
            {}
        )
        self.assertEqual(
            server.get_config(user_two, "config").get_value(),
            new_override
        )
        self.assertEqual(
            server.get_config(StatsigUser("anyuser"), "config").get_value(),
            new_override_2
        )

        # remove user override first
        server.remove_config_override("config", "123")
        # user one should now use global override
        self.assertEqual(
            server.get_config(user_one, "config").get_value(),
            new_override_2,
        )

        # remove global override
        server.remove_config_override("config")
        # user one should now have no override
        self.assertEqual(
            server.get_config(user_one, "config").get_value(),
            {}
        )

        # remove all overrides
        server.remove_all_overrides()
        self.assertEqual(
            server.get_config(user_two, "config").get_value(),
            {}
        )

        # try removing one that doesn't exist
        server.remove_config_override("fake_config_non_existent")
