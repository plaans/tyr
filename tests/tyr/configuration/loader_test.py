from pathlib import Path

import pytest
import tests.tyr.planners.fixtures.configuration as config_module
from unittest.mock import MagicMock, Mock, patch

from tyr.configuration.loader import load_config


class TestLoader:
    @patch("builtins.open")
    @patch("tyr.configuration")
    @patch("pathlib.Path.exists")
    @patch("yaml.safe_load")
    @pytest.mark.parametrize("name", ["planners", "domains"])
    def test_load_config_loads_local_file_if_present(
        self, mock_yaml, mock_path, mock_module, mock_open, name
    ):
        mock_module.__path__ = config_module.__path__
        mock_open.return_value.__enter__.return_value.read.return_value = ""
        mock_path.side_effect = [True, True]
        mock_yaml.return_value = Mock()
        file = (Path(config_module.__path__[0]) / f"{name}.yaml").resolve()
        result = load_config(name)
        mock_open.assert_called_once_with(file, "r", encoding="utf-8")
        assert result == mock_yaml.return_value

    @patch("builtins.open")
    @patch("tyr.configuration")
    @patch("pathlib.Path.exists")
    @patch("yaml.safe_load")
    @pytest.mark.parametrize("name", ["planners", "domains"])
    def test_load_config_loads_example_file_if_local_is_absent(
        self, mock_yaml, mock_path, mock_module, mock_open, name
    ):
        mock_module.__path__ = config_module.__path__
        mock_open.return_value.__enter__.return_value.read.return_value = ""
        mock_path.side_effect = [False, True]
        mock_yaml.return_value = Mock()
        file = (Path(config_module.__path__[0]) / f"{name}.example.yaml").resolve()
        result = load_config(name)
        mock_open.assert_called_once_with(file, "r", encoding="utf-8")
        assert result == mock_yaml.return_value

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_config_loads_specific_file_if_provided(self, mock_yaml, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = ""
        mock_yaml.return_value = Mock()
        file = MagicMock()
        result = load_config("", file)
        mock_open.assert_called_once_with(file, "r", encoding="utf-8")
        assert result == mock_yaml.return_value
