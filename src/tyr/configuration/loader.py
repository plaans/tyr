from pathlib import Path
from typing import Any

import yaml


def load_config(name: str) -> Any:
    """
    Loads a configuration file from the `tyr.configuration` module.

    First, it tries to load the `name`.yaml file.
    If it does not exist, it tries to load the `name`.example.yaml file.

    Args:
        name (str): Name of the configuration file.

    Returns:
        Any: The content of the file.
    """
    import tyr.configuration as config_module  # pylint: disable=import-outside-toplevel

    config_file = (Path(config_module.__path__[0]) / f"{name}.yaml").resolve()
    if not config_file.exists():
        config_file = config_file.parent / f"{name}.example.yaml"
    with open(config_file, "r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    return content


__all__ = ["load_config"]
