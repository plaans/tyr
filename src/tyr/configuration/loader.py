from pathlib import Path
from typing import Any, Optional

import yaml


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
    # pylint: disable=import-outside-toplevel, cyclic-import
    import tyr.configuration as config_module

    if path is not None:
        config_file = path
    else:
        config_file = (Path(config_module.__path__[0]) / f"{name}.yaml").resolve()
        if not config_file.exists():
            config_file = config_file.parent / f"{name}.example.yaml"

    with open(config_file, "r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    return content


__all__ = ["load_config"]
