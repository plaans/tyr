from pathlib import Path
from typing import Any, Optional

import yaml

from .matrix_expander import expand_matrix_configurations


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
        if isinstance(path, str):
            return Path(path)
        return path

    config_file = (Path(config_module.__path__[0]) / f"{name}.yaml").resolve()
    if not config_file.exists():
        config_file = config_file.parent / f"{name}.example.yaml"
    return config_file


def load_config(
    name: str,
    path: Optional[Path] = None,
    expand_matrix: bool = True,
) -> Any:
    """
    Loads a configuration file from the `tyr.configuration` module.

    First, it tries to load the `name`.yaml file.
    If it does not exist, it tries to load the `name`.example.yaml file.

    Args:
        name (str): Name of the configuration file.
        path (Optional[Path], optional): Path to the file. Defaults to None.
            If provided, it will load the configuration from this file and ignore `name` parameter.
        expand_matrix (bool, optional): Whether to expand matrix configurations. Defaults to True.

    Returns:
        Any: The content of the file.
    """
    with open(get_config_file(name, path), "r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    # Expand matrix configurations if requested and content is a list
    if expand_matrix and isinstance(content, list):
        content = expand_matrix_configurations(content)

    return content


__all__ = ["load_config"]
