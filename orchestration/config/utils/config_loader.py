from pathlib import Path

import yaml


CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "fhir_resources.yaml"
)


def load_fhir_resources() -> list[str]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config["resources"]