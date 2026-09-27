from unittest.mock import patch
import pytest
from mealie.core.logger.config import _load_config, configured_logger, log_config


def test_load_config_with_substitutions(tmp_path):
    config_file = tmp_path / "test_config.json"
    config_file.write_text('{"path": "${BASE_PATH}/logs"}')

    result = _load_config(config_file, substitutions={"BASE_PATH": "/app"})
    assert result == {"path": "/app/logs"}


def test_load_config_without_substitutions(tmp_path):
    config_file = tmp_path / "test_config.json"
    config_file.write_text('{"level": "INFO"}')

    result = _load_config(config_file)
    assert result == {"level": "INFO"}


def test_log_config_unconfigured_raises_error():
    with patch("mealie.core.logger.config.__conf", None):
        with pytest.raises(ValueError, match="logger not configured"):
            log_config()


def test_log_config_success():
    mock_conf = {"key": "value"}
    with patch("mealie.core.logger.config.__conf", mock_conf):
        assert log_config() == mock_conf


def test_configured_logger_with_config_override(tmp_path):
    custom_config = tmp_path / "custom.json"
    custom_config.write_text('{"version": 1}')

    with (
        patch("mealie.core.logger.config.logging_config.dictConfig") as mock_dict_config,
        patch("mealie.core.logger.config.logging.getLogger") as mock_get_logger,
    ):
        configured_logger(mode="production", config_override=custom_config)
        mock_dict_config.assert_called_once_with(config={"version": 1})
        mock_get_logger.assert_called_once()


def test_configured_logger_invalid_mode():
    with pytest.raises(ValueError, match="Invalid mode"):
        configured_logger(mode="invalid_mode")


def test_configured_logger_modes():
    with (
        patch("mealie.core.logger.config._load_config") as mock_load,
        patch("mealie.core.logger.config.logging_config.dictConfig"),
        patch("mealie.core.logger.config.logging.getLogger"),
    ):
        mock_load.return_value = {"version": 1}
        configured_logger(mode="development")
        configured_logger(mode="testing")


def test_configured_logger_production_mode():
    with (
        patch("mealie.core.logger.config._load_config") as mock_load,
        patch("mealie.core.logger.config.logging_config.dictConfig"),
        patch("mealie.core.logger.config.logging.getLogger"),
    ):
        mock_load.return_value = {"version": 1}
        configured_logger(mode="production")
