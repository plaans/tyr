"""Tests for matrix configuration validation."""


from tyr.configuration.matrix_config import validate_matrix_configuration


class TestMatrixConfigValidation:
    """Test matrix configuration validation."""

    def test_valid_matrix_configuration(self):
        """Test validation of valid matrix configuration."""
        config = {
            "name": "planner-{variant}-{strategy}",
            "matrix": {"variant": ["a", "b"], "strategy": ["first", "fallback"]},
            "env": {"VARIANT": "{variant}", "STRATEGY": "{strategy}"},
        }

        errors = validate_matrix_configuration(config)
        assert errors == []

    def test_non_matrix_configuration(self):
        """Test validation of non-matrix configuration (should pass)."""
        config = {"name": "simple-planner", "env": {"VAR": "value"}}

        errors = validate_matrix_configuration(config)
        assert errors == []

    def test_unused_matrix_variables(self):
        """Test detection of unused matrix variables."""
        config = {
            "name": "planner-{variant}",
            "matrix": {"variant": ["a", "b"], "unused_var": ["x", "y"]},
            "env": {"VARIANT": "{variant}"},
        }

        errors = validate_matrix_configuration(config)
        assert len(errors) == 1
        assert "unused_var" in errors[0]
        assert "Unused matrix variables" in errors[0]

    def test_undefined_variable_references(self):
        """Test detection of undefined variable references."""
        config = {
            "name": "planner-{variant}",
            "matrix": {"variant": ["a", "b"]},
            "env": {"VARIANT": "{variant}", "UNDEFINED": "{missing_var}"},
        }

        errors = validate_matrix_configuration(config)
        assert len(errors) == 1
        assert "missing_var" in errors[0]
        assert "Undefined variable references" in errors[0]

    def test_name_without_placeholders(self):
        """Test detection of matrix name without variable placeholders."""
        config = {
            "name": "static-planner-name",
            "matrix": {"variant": ["a", "b"]},
            "env": {"VARIANT": "{variant}"},
        }

        errors = validate_matrix_configuration(config)
        assert len(errors) == 1  # Only static name (variant is used in env)
        assert any(
            "name should contain variable placeholders" in error for error in errors
        )

    def test_nested_variable_references(self):
        """Test validation with nested variable references."""
        config = {
            "name": "planner-{strategy.name}",
            "matrix": {
                "strategy": [
                    {"name": "first", "value": "first_solution"},
                    {"name": "fallback", "value": "timeout_fallback"},
                ]
            },
            "env": {"STRATEGY": "{strategy.value}", "STRATEGY_NAME": "{strategy.name}"},
        }

        errors = validate_matrix_configuration(config)
        assert errors == []

    def test_multiple_validation_errors(self):
        """Test configuration with multiple validation errors."""
        config = {
            "name": "static-name",
            "matrix": {"variant": ["a", "b"], "unused1": ["x"], "unused2": ["y"]},
            "env": {"VARIANT": "{variant}", "MISSING": "{missing_var}"},
        }

        errors = validate_matrix_configuration(config)
        assert len(errors) == 3

        # Check that all expected errors are present
        error_text = " ".join(errors)
        assert "unused1" in error_text
        assert "unused2" in error_text
        assert "missing_var" in error_text
        assert "variable placeholders" in error_text

    def test_with_when_condition(self):
        """Test validation with 'when' condition in matrix."""
        config = {
            "name": "planner-{variant}",
            "matrix": {"variant": ["a", "b"], "when": "variant == 'a'"},
            "env": {"VARIANT": "{variant}"},
        }

        errors = validate_matrix_configuration(config)
        assert errors == []  # 'when' should be ignored in validation
