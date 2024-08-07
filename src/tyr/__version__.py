import importlib.metadata
from pathlib import Path

import toml


def load_version():
    """
    Load the version from the pyproject.toml file if it exists,
    otherwise use importlib.metadata.version
    """
    pyproject_toml_file = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
        pyproject_toml = toml.load(pyproject_toml_file)
        name = pyproject_toml["project"]["name"]
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            return toml.load(pyproject_toml_file)["project"]["version"] + "-dev"
    else:
        return importlib.metadata.version("tyr")


__version__ = load_version()
