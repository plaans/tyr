"""Tests for conditional matrix configuration functionality."""

import pytest

from tyr.configuration.matrix_expander import MatrixExpander


class TestConditionalMatrixExpansion:
    """Test conditional expressions in matrix configurations."""
    
    def test_simple_string_conditional(self):
        """Test basic string conditional expression."""
        expander = MatrixExpander()
        configs = [{
            "name": "planner-{type}",
            "matrix": {
                "type": ["flexible", "strict"]
            },
            "env": {
                "SYMMETRY": "{type == 'flexible' ? 'psp' : 'simple'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 2
        
        flexible_config = next(c for c in result if c["name"] == "planner-flexible")
        assert flexible_config["env"]["SYMMETRY"] == "psp"
        
        strict_config = next(c for c in result if c["name"] == "planner-strict")
        assert strict_config["env"]["SYMMETRY"] == "simple"
    
    def test_numeric_conditional(self):
        """Test conditional with numeric comparisons."""
        expander = MatrixExpander()
        configs = [{
            "name": "config-{count}",
            "matrix": {
                "count": [1, 5, 10]
            },
            "env": {
                "LEVEL": "{count > 5 ? 'high' : 'low'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 3
        
        config_1 = next(c for c in result if c["name"] == "config-1")
        assert config_1["env"]["LEVEL"] == "low"
        
        config_5 = next(c for c in result if c["name"] == "config-5")
        assert config_5["env"]["LEVEL"] == "low"
        
        config_10 = next(c for c in result if c["name"] == "config-10")
        assert config_10["env"]["LEVEL"] == "high"
    
    def test_nested_property_conditional(self):
        """Test conditional with nested property access."""
        expander = MatrixExpander()
        configs = [{
            "name": "planner-{strategy}",
            "matrix": {
                "strategy": [
                    {"name": "fast", "timeout": 30},
                    {"name": "thorough", "timeout": 300}
                ]
            },
            "env": {
                "MODE": "{strategy.timeout > 100 ? 'extended' : 'quick'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 2
        
        fast_config = next(c for c in result if c["name"] == "planner-fast")
        assert fast_config["env"]["MODE"] == "quick"
        
        thorough_config = next(c for c in result if c["name"] == "planner-thorough")
        assert thorough_config["env"]["MODE"] == "extended"
    
    def test_multiple_operators(self):
        """Test different comparison operators."""
        expander = MatrixExpander()
        configs = [{
            "name": "test-{value}",
            "matrix": {
                "value": [1, 3, 5]
            },
            "env": {
                "EQUAL_3": "{value == 3 ? 'yes' : 'no'}",
                "NOT_EQUAL_3": "{value != 3 ? 'yes' : 'no'}",
                "LESS_THAN_4": "{value < 4 ? 'yes' : 'no'}",
                "GREATER_EQUAL_3": "{value >= 3 ? 'yes' : 'no'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 3
        
        # Test value = 3
        config_3 = next(c for c in result if c["name"] == "test-3")
        assert config_3["env"]["EQUAL_3"] == "yes"
        assert config_3["env"]["NOT_EQUAL_3"] == "no"
        assert config_3["env"]["LESS_THAN_4"] == "yes"
        assert config_3["env"]["GREATER_EQUAL_3"] == "yes"
        
        # Test value = 1
        config_1 = next(c for c in result if c["name"] == "test-1")
        assert config_1["env"]["EQUAL_3"] == "no"
        assert config_1["env"]["NOT_EQUAL_3"] == "yes"
        assert config_1["env"]["LESS_THAN_4"] == "yes"
        assert config_1["env"]["GREATER_EQUAL_3"] == "no"
    
    def test_mixed_conditionals_and_variables(self):
        """Test mixing conditionals and regular variable substitution."""
        expander = MatrixExpander()
        configs = [{
            "name": "planner-{type}-{mode}",
            "matrix": {
                "type": ["fast", "slow"],
                "mode": ["debug", "release"]
            },
            "env": {
                "TYPE": "{type}",
                "OPTIMIZATION": "{mode == 'release' ? 'O3' : 'O0'}",
                "DESCRIPTION": "Running {type} with {mode == 'debug' ? 'debugging' : 'optimizations'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 4
        
        fast_debug = next(c for c in result if c["name"] == "planner-fast-debug")
        assert fast_debug["env"]["TYPE"] == "fast"
        assert fast_debug["env"]["OPTIMIZATION"] == "O0"
        assert fast_debug["env"]["DESCRIPTION"] == "Running fast with debugging"
        
        slow_release = next(c for c in result if c["name"] == "planner-slow-release")
        assert slow_release["env"]["TYPE"] == "slow"
        assert slow_release["env"]["OPTIMIZATION"] == "O3"
        assert slow_release["env"]["DESCRIPTION"] == "Running slow with optimizations"
    
    def test_boolean_conditionals(self):
        """Test conditionals with boolean values."""
        expander = MatrixExpander()
        configs = [{
            "name": "config-{enabled}",
            "matrix": {
                "enabled": [True, False]
            },
            "env": {
                "STATUS": "{enabled == true ? 'active' : 'inactive'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 2
        
        enabled_config = next(c for c in result if c["name"] == "config-True")
        assert enabled_config["env"]["STATUS"] == "active"
        
        disabled_config = next(c for c in result if c["name"] == "config-False")
        assert disabled_config["env"]["STATUS"] == "inactive"
    
    def test_invalid_conditional_syntax(self):
        """Test that invalid conditional syntax is left unchanged."""
        expander = MatrixExpander()
        configs = [{
            "name": "test",
            "matrix": {
                "var": ["value"]
            },
            "env": {
                "INVALID_1": "{var == 'value' ?}",  # Missing false value
                "INVALID_2": "{var == 'value'}",    # Missing conditional parts
                "INVALID_3": "{? 'true' : 'false'}" # Missing condition
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 1
        config = result[0]
        
        # Invalid conditionals should be left as-is
        assert config["env"]["INVALID_1"] == "{var == 'value' ?}"
        assert config["env"]["INVALID_2"] == "{var == 'value'}"  # Invalid conditional, left unchanged
        assert config["env"]["INVALID_3"] == "{? 'true' : 'false'}"
    
    def test_conditional_with_missing_variable(self):
        """Test conditional with undefined variable reference."""
        expander = MatrixExpander()
        configs = [{
            "name": "test",
            "matrix": {
                "var": ["value"]
            },
            "env": {
                "RESULT": "{missing_var == 'value' ? 'yes' : 'no'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 1
        config = result[0]
        
        # Should fall back to original expression when variable is missing
        assert config["env"]["RESULT"] == "{missing_var == 'value' ? 'yes' : 'no'}"
    
    def test_quoted_strings_in_conditionals(self):
        """Test that quoted strings are handled correctly in conditionals."""
        expander = MatrixExpander()
        configs = [{
            "name": "test-{type}",
            "matrix": {
                "type": ["option1", "option2"]
            },
            "env": {
                "SINGLE_QUOTES": "{type == 'option1' ? 'result1' : 'result2'}",
                "DOUBLE_QUOTES": '{type == "option1" ? "result1" : "result2"}',
                "MIXED_QUOTES": "{type == 'option1' ? \"result1\" : 'result2'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        
        assert len(result) == 2
        
        option1_config = next(c for c in result if c["name"] == "test-option1")
        assert option1_config["env"]["SINGLE_QUOTES"] == "result1"
        assert option1_config["env"]["DOUBLE_QUOTES"] == "result1"
        assert option1_config["env"]["MIXED_QUOTES"] == "result1"
        
        option2_config = next(c for c in result if c["name"] == "test-option2")
        assert option2_config["env"]["SINGLE_QUOTES"] == "result2"
        assert option2_config["env"]["DOUBLE_QUOTES"] == "result2"
        assert option2_config["env"]["MIXED_QUOTES"] == "result2"


class TestConditionalOperatorParsing:
    """Test conditional operator parsing and evaluation."""
    
    def test_operator_precedence(self):
        """Test that operators are found in correct precedence order."""
        expander = MatrixExpander()
        
        # Test that <= is found before <
        configs = [{
            "name": "test",
            "matrix": {"x": [5]},
            "env": {"RESULT": "{x <= 5 ? 'yes' : 'no'}"}
        }]
        
        result = expander.expand_configurations(configs)
        assert result[0]["env"]["RESULT"] == "yes"
        
        # Test that >= is found before >
        configs = [{
            "name": "test", 
            "matrix": {"x": [5]},
            "env": {"RESULT": "{x >= 5 ? 'yes' : 'no'}"}
        }]
        
        result = expander.expand_configurations(configs)
        assert result[0]["env"]["RESULT"] == "yes"
    
    def test_whitespace_handling(self):
        """Test that whitespace around operators and values is handled correctly."""
        expander = MatrixExpander()
        configs = [{
            "name": "test",
            "matrix": {"x": ["value"]},
            "env": {
                "NO_SPACES": "{x=='value'?'yes':'no'}",
                "WITH_SPACES": "{ x == 'value' ? 'yes' : 'no' }",
                "MIXED_SPACES": "{x== 'value'? 'yes' :'no'}"
            }
        }]
        
        result = expander.expand_configurations(configs)
        config = result[0]
        
        assert config["env"]["NO_SPACES"] == "yes"
        assert config["env"]["WITH_SPACES"] == "yes" 
        assert config["env"]["MIXED_SPACES"] == "yes"