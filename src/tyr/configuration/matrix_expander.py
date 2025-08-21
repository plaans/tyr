"""Matrix configuration expansion for planner configurations."""

from itertools import product
from typing import Any, Dict, List, Union
import re
import operator


# pylint: disable=too-few-public-methods
class MatrixExpander:
    """Expands matrix definitions in configuration to generate all combinations."""

    def expand_configurations(
        self, configurations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Expand matrix configurations to generate all combinations.

        Args:
            configurations: List of configuration dictionaries that may contain matrix definitions

        Returns:
            List of expanded configurations with matrix definitions resolved
        """
        expanded = []

        for config in configurations:
            if "matrix" in config:
                expanded.extend(self._expand_single_matrix(config))
            else:
                expanded.append(config)

        return expanded

    # pylint: disable=too-many-locals
    def _expand_single_matrix(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Expand a single configuration with matrix definition.

        Args:
            config: Configuration dictionary containing matrix definition

        Returns:
            List of expanded configurations
        """
        matrix = config["matrix"]
        base_config = {k: v for k, v in config.items() if k != "matrix"}

        # Extract matrix variables and their values, converting complex objects to MatrixValue
        matrix_vars = {}
        for key, values in matrix.items():
            if isinstance(values, list):
                processed_values = []
                for value in values:
                    if isinstance(value, dict) and "name" in value:
                        # Convert to MatrixValue-like object
                        from .matrix_config import MatrixValue

                        name = value["name"]
                        val = value.get("value", name)
                        properties = {
                            k: v for k, v in value.items() if k not in ["name", "value"]
                        }
                        processed_values.append(MatrixValue(name, val, properties))
                    else:
                        processed_values.append(value)
                matrix_vars[key] = processed_values
            else:
                matrix_vars[key] = [values]

        # Generate all combinations
        expanded_configs = []
        var_names = list(matrix_vars.keys())

        for combination in product(*[matrix_vars[var] for var in var_names]):
            # Create variable substitution context
            var_context = {}
            for var_name, value in zip(var_names, combination):
                var_context[var_name] = value

            # Create expanded configuration
            expanded_config = self._substitute_variables(base_config, var_context)
            expanded_configs.append(expanded_config)

        return expanded_configs

    def _substitute_variables(self, obj: Any, context: Dict[str, Any]) -> Any:
        """
        Recursively substitute variables in configuration object.

        Args:
            obj: Object to perform substitution on
            context: Variable substitution context

        Returns:
            Object with variables substituted
        """
        if isinstance(obj, str):
            return self._substitute_string(obj, context)
        elif isinstance(obj, dict):
            return {
                key: self._substitute_variables(value, context)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._substitute_variables(item, context) for item in obj]
        else:
            return obj

    def _substitute_string(self, text: str, context: Dict[str, Any]) -> str:
        """
        Substitute variables and evaluate conditionals in a string.
        
        Supports both variable substitution ({variable}) and conditional expressions
        ({condition ? true_value : false_value}).

        Args:
            text: String to substitute variables in
            context: Variable substitution context

        Returns:
            String with variables substituted and conditionals evaluated
        """

        def replace_expression(match: re.Match[str]) -> str:
            expression = match.group(1)
            
            # Check if this is a conditional expression
            if "?" in expression and ":" in expression:
                return self._evaluate_conditional(expression, context)
            else:
                # Regular variable substitution
                return self._evaluate_variable(expression, context)

        # Replace {expression} patterns (variables or conditionals)
        return re.sub(r"\{([^}]+)\}", replace_expression, text)
    
    def _evaluate_variable(self, var_path: str, context: Dict[str, Any]) -> str:
        """
        Evaluate a variable reference like 'variable' or 'variable.property'.
        
        Args:
            var_path: Variable path to evaluate
            context: Variable substitution context
            
        Returns:
            String representation of the variable value
        """
        parts = var_path.split(".")

        try:
            value = context[parts[0]]

            # Handle nested property access
            for part in parts[1:]:
                if isinstance(value, dict):
                    value = value[part]
                else:
                    value = getattr(value, part)

            return str(value)
        except (KeyError, AttributeError):
            # If variable not found, leave placeholder unchanged
            return "{" + var_path + "}"
    
    def _evaluate_conditional(self, expression: str, context: Dict[str, Any]) -> str:
        """
        Evaluate a conditional expression like 'var == "value" ? "A" : "B"'.
        
        Args:
            expression: Conditional expression to evaluate
            context: Variable substitution context
            
        Returns:
            String result of the conditional evaluation
        """
        try:
            # Parse conditional: condition ? true_value : false_value
            question_idx = expression.find("?")
            colon_idx = expression.rfind(":")
            
            if question_idx == -1 or colon_idx == -1 or colon_idx <= question_idx:
                # Invalid conditional syntax, return as-is
                return "{" + expression + "}"
            
            condition_str = expression[:question_idx].strip()
            true_value = expression[question_idx + 1:colon_idx].strip()
            false_value = expression[colon_idx + 1:].strip()
            
            # Remove quotes from values if present
            true_value = self._unquote_string(true_value)
            false_value = self._unquote_string(false_value)
            
            # Evaluate the condition
            condition_result = self._evaluate_condition(condition_str, context)
            
            return true_value if condition_result else false_value
            
        except Exception:
            # If evaluation fails, return the original expression
            return "{" + expression + "}"
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Safely evaluate a boolean condition.
        
        Supports: ==, !=, <, >, <=, >=
        
        Args:
            condition: Condition string to evaluate
            context: Variable substitution context
            
        Returns:
            Boolean result of the condition
        """
        # Define supported operators
        operators = {
            "==": operator.eq,
            "!=": operator.ne,
            "<=": operator.le,
            ">=": operator.ge,
            "<": operator.lt,
            ">": operator.gt,
        }
        
        # Find the operator
        op_found = None
        op_pos = -1
        
        for op_str in sorted(operators.keys(), key=len, reverse=True):
            pos = condition.find(op_str)
            if pos != -1:
                op_found = op_str
                op_pos = pos
                break
        
        if op_found is None:
            raise ValueError(f"No supported operator found in condition: {condition}")
        
        # Split condition into left and right parts
        left_str = condition[:op_pos].strip()
        right_str = condition[op_pos + len(op_found):].strip()
        
        # Evaluate left and right operands
        left_value = self._evaluate_operand(left_str, context)
        right_value = self._evaluate_operand(right_str, context)
        
        # Apply the operator
        return operators[op_found](left_value, right_value)
    
    def _evaluate_operand(self, operand: str, context: Dict[str, Any]) -> Union[str, int, float, bool]:
        """
        Evaluate an operand (variable reference or literal value).
        
        Args:
            operand: Operand string to evaluate
            context: Variable substitution context
            
        Returns:
            Evaluated operand value
        """
        operand = operand.strip()
        
        # Check if it's a quoted string literal
        if ((operand.startswith('"') and operand.endswith('"')) or
            (operand.startswith("'") and operand.endswith("'"))):
            return operand[1:-1]  # Remove quotes
        
        # Check if it's a number
        try:
            if "." in operand:
                return float(operand)
            else:
                return int(operand)
        except ValueError:
            pass
        
        # Check if it's a boolean
        if operand.lower() == "true":
            return True
        elif operand.lower() == "false":
            return False
        
        # Otherwise, treat as variable reference
        parts = operand.split(".")
        try:
            value = context[parts[0]]
            
            # Handle nested property access
            for part in parts[1:]:
                if isinstance(value, dict):
                    value = value[part]
                else:
                    value = getattr(value, part)
            
            return value
        except (KeyError, AttributeError):
            raise ValueError(f"Variable not found: {operand}")
    
    def _unquote_string(self, value: str) -> str:
        """
        Remove quotes from a string value if present.
        
        Args:
            value: String value that may be quoted
            
        Returns:
            Unquoted string value
        """
        value = value.strip()
        if ((value.startswith('"') and value.endswith('"')) or
            (value.startswith("'") and value.endswith("'"))):
            return value[1:-1]
        return value


def expand_matrix_configurations(
    configurations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Convenience function to expand matrix configurations.

    Args:
        configurations: List of configuration dictionaries

    Returns:
        List of expanded configurations
    """
    expander = MatrixExpander()
    return expander.expand_configurations(configurations)
