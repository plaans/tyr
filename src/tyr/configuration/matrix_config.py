"""Data models for matrix configuration definitions."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import re


@dataclass
class MatrixValue:
    """Represents a value in a matrix that can have additional properties."""

    name: str
    value: Any
    properties: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.name

    def __getattr__(self, name: str) -> Any:
        """Allow property access on matrix values."""
        if name in self.properties:
            return self.properties[name]
        elif name == "value":
            return self.value
        raise AttributeError(f"MatrixValue has no attribute '{name}'")


@dataclass
class MatrixDefinition:
    """Represents a matrix definition in configuration."""

    variables: Dict[str, List[Union[str, int, float, MatrixValue]]]
    condition: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MatrixDefinition":
        """
        Create MatrixDefinition from dictionary representation.

        Args:
            data: Dictionary containing matrix definition

        Returns:
            MatrixDefinition instance
        """
        variables = {}
        condition = data.get("when")

        for key, values in data.items():
            if key == "when":
                continue

            if not isinstance(values, list):
                values = [values]

            processed_values = []
            for value in values:
                if isinstance(value, dict) and "name" in value:
                    # Convert complex matrix value to MatrixValue
                    name = value["name"]
                    val = value.get("value", name)
                    properties = {
                        k: v for k, v in value.items() if k not in ["name", "value"]
                    }
                    processed_values.append(MatrixValue(name, val, properties))
                else:
                    processed_values.append(value)

            variables[key] = processed_values

        return cls(variables, condition)


@dataclass
class MatrixConfiguration:
    """Represents a configuration with matrix expansion capability."""

    name: str
    matrix: Optional[MatrixDefinition] = None
    base_config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MatrixConfiguration":
        """
        Create MatrixConfiguration from dictionary representation.

        Args:
            data: Dictionary containing configuration

        Returns:
            MatrixConfiguration instance
        """
        name = data["name"]
        matrix = None

        if "matrix" in data:
            matrix = MatrixDefinition.from_dict(data["matrix"])

        base_config = {k: v for k, v in data.items() if k not in ["name", "matrix"]}

        return cls(name, matrix, base_config)

    def has_matrix(self) -> bool:
        """Check if this configuration has matrix expansion."""
        return self.matrix is not None

    def get_matrix_variables(self) -> Dict[str, List[Any]]:
        """Get matrix variables for expansion."""
        if not self.has_matrix():
            return {}
        return self.matrix.variables


def validate_matrix_configuration(config: Dict[str, Any]) -> List[str]:
    """
    Validate a matrix configuration for common issues.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation error messages
    """
    errors = []

    if "matrix" not in config:
        return errors  # Not a matrix config, nothing to validate

    matrix = config["matrix"]

    # Check if matrix variables are referenced in the configuration
    matrix_vars = set(matrix.keys())
    if "when" in matrix_vars:
        matrix_vars.remove("when")

    # Find all variable references recursively
    referenced_vars = set()

    def find_variables_recursive(obj):
        """Recursively find variable references in an object."""
        if isinstance(obj, str):
            for match in re.finditer(r"\{([^}]+)\}", obj):
                var_path = match.group(1)
                base_var = var_path.split(".")[0]
                referenced_vars.add(base_var)
        elif isinstance(obj, dict):
            for value in obj.values():
                find_variables_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                find_variables_recursive(item)

    # Search for variable references in all config except matrix
    config_without_matrix = {k: v for k, v in config.items() if k != "matrix"}
    find_variables_recursive(config_without_matrix)

    # Check for unused matrix variables
    unused_vars = matrix_vars - referenced_vars
    if unused_vars:
        errors.append(f"Unused matrix variables: {unused_vars}")

    # Check for undefined variable references
    undefined_vars = referenced_vars - matrix_vars
    if undefined_vars:
        errors.append(f"Undefined variable references: {undefined_vars}")

    # Validate name template
    if "name" in config and "{" not in config["name"]:
        errors.append("Matrix configuration name should contain variable placeholders")

    return errors
