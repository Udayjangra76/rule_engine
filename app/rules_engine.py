import json
import re

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type  # "operator" or "operand"
        self.value = value  # Value of the node, e.g., "age > 30"
        self.left = left  # Left child node
        self.right = right  # Right child node

    def __repr__(self):
        return f"Node({self.type}, {self.value}, left={self.left}, right={self.right})"

    def to_dict(self):
        """Convert the Node to a dictionary representation."""
        return {
            'type': self.type,
            'value': self.value,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Node from a dictionary representation."""
        left = cls.from_dict(data['left']) if data['left'] else None
        right = cls.from_dict(data['right']) if data['right'] else None
        return cls(node_type=data['type'], value=data['value'], left=left, right=right)

def serialize_node(node):
    """Serialize a Node object to a JSON string."""
    return json.dumps(node.to_dict())

def deserialize_node(node_string):
    """Deserialize a JSON string back to a Node object."""
    node_dict = json.loads(node_string)
    return Node.from_dict(node_dict)

def precedence(op):
    if op == 'AND' or op == 'OR':
        return 1
    if op in ('>', '<', '='):
        return 2
    return 0

def apply_operator(operators, operands):
    operator = operators.pop()
    right = operands.pop()
    left = operands.pop()
    operands.append(Node("operator", operator, left, right))

def create_rule(rule_string):
    tokens = re.findall(r"\(|\)|\w+|>|<|=|AND|OR|'[^']*'", rule_string)
    operands = []
    operators = []

    for token in tokens:
        if token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, operands)
            operators.pop()  # Remove '(' from stack
        elif token in ('AND', 'OR', '>', '<', '='):
            while (operators and precedence(operators[-1]) >= precedence(token)):
                apply_operator(operators, operands)
            operators.append(token)
        else:  # Operand
            operands.append(Node("operand", token))

    while operators:
        apply_operator(operators, operands)

    return serialize_node(operands[-1])  # The root of the AST

def combine_rules(rules):
    root = None
    for rule_string in rules:
        rule_ast = deserialize_node(rule_string.rule_string)
        if not root:
            root = rule_ast
        else:
            # Create a new root with "AND" operator, combining the current root and new rule AST
            root = Node("operator", "AND", root, rule_ast)
    return serialize_node(root)

def evaluate_expression(expression, data):
    """ Evaluate an expression node. """
    if expression.type == "operand":
        # Operand nodes should not be evaluated directly here
        return expression.value
    elif expression.type == "operator":
        # Evaluate left and right nodes recursively
        left_value = evaluate_expression(expression.left, data)
        right_value = evaluate_expression(expression.right, data)
        return evaluate_operator(expression.value, left_value, right_value, data)

def evaluate_operator(operator, left_value, right_value, data):
    """ Evaluate an operator node with left and right values. """
    if operator == 'AND':
        return left_value and right_value
    elif operator == 'OR':
        return left_value or right_value
    elif operator in ('>', '<', '='):
        # Apply comparison directly
        if not isinstance(left_value, (int, str)) or not isinstance(right_value, (int, str)):
            raise ValueError("Comparison requires numeric or string operands")
        return apply_comparison(operator, left_value, right_value, data)
    else:
        raise ValueError(f"Unknown operator '{operator}'")

def apply_comparison(operator, left, right, data):
    """ Apply a comparison operator with type handling. """
    # Get the actual values from the data dictionary
    if left in data:
        left_value = data[left]
    else:
        raise ValueError(f"Field '{left}' not found in data")

    # Ensure that the right operand is of the correct type
    try:
        right_value = int(right)  # Try to convert to integer
    except ValueError:
        right_value = right.strip().strip("'")  # If conversion fails, keep it as string
    
    # Compare values based on the operator
    if operator == '>':
        return left_value > right_value
    elif operator == '<':
        return left_value < right_value
    elif operator == '=':
        # For equality, ensure both values are of the same type
        if isinstance(left_value, str) and isinstance(right_value, str):
            # Compare strings lexicographically
            return left_value.lower() == right_value.lower()
        elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            # Compare numerics
            return left_value == right_value
        else:
            raise ValueError("Equality comparison requires both operands to be of the same type")
    else:
        raise ValueError(f"Unknown comparison operator '{operator}'")

def evaluate_rule(root, data):
    """ Evaluate the entire rule by traversing the AST. """
    return evaluate_expression(deserialize_node(root), data)

