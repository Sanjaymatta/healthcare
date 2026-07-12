from pathlib import Path
import logging
import logging.config

import yaml


class LoggerManager:
    """
    Loads application logging configuration and
    provides configured logger instances.
    """

    _configured = False

    @classmethod
    def configure(cls) -> None:
        """
        Configure logging only once.
        """

        if cls._configured:
            return

        project_root = Path(__file__).resolve().parents[2]

        config_path = project_root / "config" / "logging.yaml"

        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        logging.config.dictConfig(config)

        cls._configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger.
    """

    LoggerManager.configure()

    return logging.getLogger(name)