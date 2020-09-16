class TestConfig:
    """
    Class to test the Config object.

    Public attributes:
        config (Config object): Config object to test
    """

    def test_get_can_fetch_nested_items_with_dots(self, config):
        config.data = {
            "first": {"second": "value"},
        }

        assert config.get("first.second") == "value"

    def test_set_can_set_nested_items_with_dots(self, config):
        config.set("storage.type", "tinydb")
        assert config.data["storage"]["type"] == "tinydb"

    def test_config_can_fetch_nested_items_with_dictionary_notation(self, config):
        config.data = {
            "first": {"second": "value"},
        }

        assert config["first"]["second"] == "value"

    def test_config_load(self, config):
        config.load()
        assert config.data["verbose"] == "info"

    def test_save_config(self, config):
        config.data = {"a": "b"}

        config.save()

        with open(config.config_path, "r") as f:
            assert "a:" in f.read()
