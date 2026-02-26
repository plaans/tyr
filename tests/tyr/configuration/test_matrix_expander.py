"""Tests for matrix configuration expansion."""

import pytest

from tyr.configuration.matrix_config import (
    MatrixConfiguration,
    MatrixDefinition,
    MatrixValue,
)
from tyr.configuration.matrix_expander import (
    MatrixExpander,
    expand_matrix_configurations,
)


class TestMatrixExpander:
    """Test matrix expansion functionality."""

    def test_no_matrix_configuration(self):
        """Test that configurations without matrix are returned unchanged."""
        expander = MatrixExpander()
        configs = [
            {"name": "simple-planner", "env": {"VAR": "value"}},
            {"name": "another-planner", "problems": {"test": "base"}},
        ]
        result = expander.expand_configurations(configs)
        assert result == configs

    def test_simple_matrix_expansion(self):
        """Test basic matrix expansion with simple values."""
        expander = MatrixExpander()
        configs = [
            {
                "name": "planner-{variant}",
                "matrix": {"variant": ["a", "b", "c"]},
                "env": {"VARIANT": "{variant}"},
            }
        ]

        result = expander.expand_configurations(configs)

        assert len(result) == 3
        expected_names = ["planner-a", "planner-b", "planner-c"]
        actual_names = [config["name"] for config in result]
        assert actual_names == expected_names

        # Check environment variable substitution
        for i, variant in enumerate(["a", "b", "c"]):
            assert result[i]["env"]["VARIANT"] == variant

    def test_multi_dimension_matrix(self):
        """Test matrix expansion with multiple dimensions."""
        expander = MatrixExpander()
        configs = [
            {
                "name": "planner-{type}-{strategy}",
                "matrix": {
                    "type": ["causal", "flexible"],
                    "strategy": ["first", "fallback"],
                },
                "env": {"TYPE": "{type}", "STRATEGY": "{strategy}"},
            }
        ]

        result = expander.expand_configurations(configs)

        assert len(result) == 4
        expected = [
            ("planner-causal-first", "causal", "first"),
            ("planner-causal-fallback", "causal", "fallback"),
            ("planner-flexible-first", "flexible", "first"),
            ("planner-flexible-fallback", "flexible", "fallback"),
        ]

        for i, (name, type_val, strategy_val) in enumerate(expected):
            assert result[i]["name"] == name
            assert result[i]["env"]["TYPE"] == type_val
            assert result[i]["env"]["STRATEGY"] == strategy_val

    def test_matrix_value_objects(self):
        """Test matrix expansion with MatrixValue objects."""
        expander = MatrixExpander()
        configs = [
            {
                "name": "planner-{strategy}",
                "matrix": {
                    "strategy": [
                        {"name": "first", "value": "first_solution"},
                        {"name": "fallback", "value": "timeout_fallback"},
                    ]
                },
                "env": {"STRATEGY": "{strategy.value}", "STRATEGY_NAME": "{strategy}"},
            }
        ]

        result = expander.expand_configurations(configs)

        assert len(result) == 2
        assert result[0]["name"] == "planner-first"
        assert result[0]["env"]["STRATEGY"] == "first_solution"
        assert result[0]["env"]["STRATEGY_NAME"] == "first"

        assert result[1]["name"] == "planner-fallback"
        assert result[1]["env"]["STRATEGY"] == "timeout_fallback"
        assert result[1]["env"]["STRATEGY_NAME"] == "fallback"

    def test_nested_object_substitution(self):
        """Test variable substitution in nested objects."""
        expander = MatrixExpander()
        configs = [
            {
                "name": "planner-{variant}",
                "matrix": {"variant": ["a", "b"]},
                "nested": {
                    "inner": {
                        "value": "variant-{variant}",
                        "list": ["item-{variant}", "static"],
                    }
                },
            }
        ]

        result = expander.expand_configurations(configs)

        assert len(result) == 2
        assert result[0]["nested"]["inner"]["value"] == "variant-a"
        assert result[0]["nested"]["inner"]["list"] == ["item-a", "static"]
        assert result[1]["nested"]["inner"]["value"] == "variant-b"
        assert result[1]["nested"]["inner"]["list"] == ["item-b", "static"]

    def test_single_value_matrix(self):
        """Test matrix with single values (should still work)."""
        expander = MatrixExpander()
        configs = [
            {
                "name": "planner-{variant}",
                "matrix": {"variant": "single"},
                "env": {"VARIANT": "{variant}"},
            }
        ]

        result = expander.expand_configurations(configs)

        assert len(result) == 1
        assert result[0]["name"] == "planner-single"
        assert result[0]["env"]["VARIANT"] == "single"

    def test_missing_variable_reference(self):
        """Test that missing variable references are left unchanged."""
        expander = MatrixExpander()
        configs = [
            {
                "name": "planner-{variant}",
                "matrix": {"variant": ["a"]},
                "env": {"VARIANT": "{variant}", "MISSING": "{missing_var}"},
            }
        ]

        result = expander.expand_configurations(configs)

        assert len(result) == 1
        assert result[0]["env"]["VARIANT"] == "a"
        assert result[0]["env"]["MISSING"] == "{missing_var}"

    def test_mixed_matrix_and_non_matrix_configs(self):
        """Test expansion with mix of matrix and regular configurations."""
        expander = MatrixExpander()
        configs = [
            {"name": "regular-planner", "env": {"VAR": "value"}},
            {
                "name": "matrix-planner-{variant}",
                "matrix": {"variant": ["a", "b"]},
                "env": {"VARIANT": "{variant}"},
            },
            {"name": "another-regular", "env": {"OTHER": "other"}},
        ]

        result = expander.expand_configurations(configs)

        assert len(result) == 4
        assert result[0]["name"] == "regular-planner"
        assert result[1]["name"] == "matrix-planner-a"
        assert result[2]["name"] == "matrix-planner-b"
        assert result[3]["name"] == "another-regular"


class TestMatrixValue:
    """Test MatrixValue functionality."""

    def test_matrix_value_creation(self):
        """Test creating MatrixValue objects."""
        value = MatrixValue("test", "test_value", {"prop": "property"})

        assert value.name == "test"
        assert value.value == "test_value"
        assert value.properties == {"prop": "property"}
        assert str(value) == "test"

    def test_matrix_value_property_access(self):
        """Test property access on MatrixValue."""
        value = MatrixValue("test", "test_value", {"prop": "property", "num": 42})

        assert value.prop == "property"
        assert value.num == 42
        assert value.value == "test_value"

    def test_matrix_value_missing_property(self):
        """Test accessing missing property raises AttributeError."""
        value = MatrixValue("test", "test_value")

        with pytest.raises(AttributeError):
            _ = value.missing_property


class TestMatrixDefinition:
    """Test MatrixDefinition functionality."""

    def test_from_dict_simple(self):
        """Test creating MatrixDefinition from simple dictionary."""
        data = {"variant": ["a", "b", "c"], "type": ["x", "y"]}

        definition = MatrixDefinition.from_dict(data)

        assert "variant" in definition.variables
        assert "type" in definition.variables
        assert definition.variables["variant"] == ["a", "b", "c"]
        assert definition.variables["type"] == ["x", "y"]
        assert definition.condition is None

    def test_from_dict_with_complex_values(self):
        """Test creating MatrixDefinition with complex values."""
        data = {
            "strategy": [
                {"name": "first", "value": "first_solution", "timeout": 30},
                {"name": "fallback", "value": "timeout_fallback", "timeout": 60},
            ]
        }

        definition = MatrixDefinition.from_dict(data)

        assert len(definition.variables["strategy"]) == 2

        first_strategy = definition.variables["strategy"][0]
        assert isinstance(first_strategy, MatrixValue)
        assert first_strategy.name == "first"
        assert first_strategy.value == "first_solution"
        assert first_strategy.timeout == 30

        fallback_strategy = definition.variables["strategy"][1]
        assert isinstance(fallback_strategy, MatrixValue)
        assert fallback_strategy.name == "fallback"
        assert fallback_strategy.value == "timeout_fallback"
        assert fallback_strategy.timeout == 60

    def test_from_dict_with_condition(self):
        """Test creating MatrixDefinition with condition."""
        data = {"variant": ["a", "b"], "when": "variant == 'a'"}

        definition = MatrixDefinition.from_dict(data)

        assert definition.condition == "variant == 'a'"
        assert "when" not in definition.variables


class TestMatrixConfiguration:
    """Test MatrixConfiguration functionality."""

    def test_from_dict_with_matrix(self):
        """Test creating MatrixConfiguration with matrix."""
        data = {
            "name": "planner-{variant}",
            "matrix": {"variant": ["a", "b"]},
            "env": {"VAR": "{variant}"},
        }

        config = MatrixConfiguration.from_dict(data)

        assert config.name == "planner-{variant}"
        assert config.has_matrix()
        assert "variant" in config.get_matrix_variables()
        assert config.base_config == {"env": {"VAR": "{variant}"}}

    def test_from_dict_without_matrix(self):
        """Test creating MatrixConfiguration without matrix."""
        data = {"name": "simple-planner", "env": {"VAR": "value"}}

        config = MatrixConfiguration.from_dict(data)

        assert config.name == "simple-planner"
        assert not config.has_matrix()
        assert config.get_matrix_variables() == {}
        assert config.base_config == {"env": {"VAR": "value"}}


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_expand_matrix_configurations_function(self):
        """Test the expand_matrix_configurations convenience function."""
        configs = [
            {
                "name": "planner-{variant}",
                "matrix": {"variant": ["a", "b"]},
                "env": {"VARIANT": "{variant}"},
            }
        ]

        result = expand_matrix_configurations(configs)

        assert len(result) == 2
        assert result[0]["name"] == "planner-a"
        assert result[1]["name"] == "planner-b"
