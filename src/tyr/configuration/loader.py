from pathlib import Path
from typing import Any, Optional

import yaml


def get_config_file(name: str, path: Optional[Path] = None) -> Path:
    """
    Returns the configuration file path.

    Args:
        name (str): Name of the configuration file.
        path (Optional[Path], optional): Path to the file. Defaults to None.
            If provided, it will load the configuration from this file and ignore `name` parameter.

    Returns:
        Path: The configuration file path.
    """
    # pylint: disable=import-outside-toplevel, cyclic-import
    import tyr.configuration as config_module

    if path is not None:
        config_file = path
    else:
        config_file = (Path(config_module.__path__[0]) / f"{name}.yaml").resolve()
        if not config_file.exists():
            config_file = config_file.parent / f"{name}.example.yaml"

    return config_file


def load_config(name: str, path: Optional[Path] = None) -> Any:
    """
    Loads a configuration file from the `tyr.configuration` module.

    First, it tries to load the `name`.yaml file.
    If it does not exist, it tries to load the `name`.example.yaml file.

    Args:
        name (str): Name of the configuration file.
        path (Optional[Path], optional): Path to the file. Defaults to None.
            If provided, it will load the configuration from this file and ignore `name` parameter.

    Returns:
        Any: The content of the file.
    """
    with open(get_config_file(name, path), "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


__all__ = ["load_config"]
