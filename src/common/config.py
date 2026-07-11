from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


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
        Load environment variables and YAML configuration.
        """

        project_root = Path(__file__).resolve().parents[2]

        # load_dotenv(project_root / ".env")

        config_path = project_root / "config" / "app_config.yaml"

        with open(config_path, "r", encoding="utf-8") as file:
            self._config = yaml.safe_load(file)

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