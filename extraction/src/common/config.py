from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from extraction.src.common.exceptions import ConfigurationError
from extraction.src.common.logger import get_logger

logger = get_logger(__name__)

class ConfigManager:
    """
    Loads and provides access to application configuration.
    """

    _instance = None
    _config: dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        """
        Load and validate application configuration.
        """

        project_root = Path(__file__).resolve().parents[2]

        # load_dotenv(project_root / ".env")

        config_path = project_root / "config" / "app_config.yaml"

        logger.info("Loading application configuration...")

        try:
            with open(config_path, "r", encoding="utf-8") as file:
                self._config = yaml.safe_load(file)

        except FileNotFoundError as e:
            raise ConfigurationError(
                f"Configuration file not found: {config_path}"
            ) from e

        except yaml.YAMLError as e:
            raise ConfigurationError(
                "Invalid YAML syntax in app_config.yaml."
            ) from e

        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}"
            ) from e


        

        if not self._config:
            raise ConfigurationError(
                "Configuration file is empty."
            )
        
        self._validate()

        logger.info("Application configuration loaded successfully.")

    def _validate(self) -> None:
        """
        Validate required configuration.
        """

        required_keys = [
            "application.name",
            "fhir.base_url",
            "aws.bucket_name",
            "snowflake.database",
            "snowflake.schema",
        ]

        for key in required_keys:
            if self.get(key) is None:
                raise ConfigurationError(
                    f"Missing configuration: {key}"
                )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Read nested configuration values.

        Example:
            config.get("fhir.base_url")
        """

        value = self._config

        for part in key.split("."):

            if isinstance(value, dict):
                value = value.get(part)

            else:
                return default

            if value is None:
                return default

        return value