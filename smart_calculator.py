import ast
import math
import operator
import re


def _clean_number(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite result")
        if value.is_integer():
            return int(value)
        return round(value, 12)
    return value


def _factorial(x):
    if x < 0 or int(x) != x or x > 170:
        raise ValueError("Invalid factorial")
    return math.factorial(int(x))


def _percent_of(percent, number):
    return percent / 100 * number


def _evaluate_node(node):
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ValueError("Invalid constant")

    if isinstance(node, ast.UnaryOp):
        value = _evaluate_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +value
        if isinstance(node.op, ast.USub):
            return -value
        raise ValueError("Invalid unary operator")

    if isinstance(node, ast.BinOp):
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)

        operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }

        operation = next(
            (fn for op_type, fn in operations.items() if isinstance(node.op, op_type)),
            None,
        )
        if operation is None:
            raise ValueError("Invalid operator")

        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent too large")

        return operation(left, right)

    if isinstance(node, ast.Name):
        constants = {"pi": math.pi, "e": math.e}
        if node.id in constants:
            return constants[node.id]
        raise ValueError("Unknown name")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
            raise ValueError("Unknown function")
        if node.keywords:
            raise ValueError("Keyword arguments not allowed")
        args = [_evaluate_node(arg) for arg in node.args]
        return FUNCTIONS[node.func.id](*args)

    raise ValueError("Unsupported expression")


def sin_deg(x):
    return math.sin(math.radians(x))


def cos_deg(x):
    return math.cos(math.radians(x))


def tan_deg(x):
    return math.tan(math.radians(x))


FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": sin_deg,
    "cos": cos_deg,
    "tan": tan_deg,
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "log": math.log,
    "log10": math.log10,
    "ln": math.log,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": _factorial,
    "fact": _factorial,
    "pow": pow,
}


def calculate(text):
    text = text.strip().lower()

    if not text:
        raise ValueError("Empty expression")

    text = text.replace("×", "*").replace("÷", "/").replace("−", "-")
    text = text.replace("π", "pi")

    # Degree notation: sin30°, cos60°, tan45°
    text = re.sub(r"\bsin\s*([+-]?\d+(?:\.\d+)?)°", r"sin(\1)", text)
    text = re.sub(r"\bcos\s*([+-]?\d+(?:\.\d+)?)°", r"cos(\1)", text)
    text = re.sub(r"\btan\s*([+-]?\d+(?:\.\d+)?)°", r"tan(\1)", text)

    # Also support sin 30, cos 60, tan 45 as degrees.
    text = re.sub(r"\bsin\s+([+-]?\d+(?:\.\d+)?)\b", r"sin(\1)", text)
    text = re.sub(r"\bcos\s+([+-]?\d+(?:\.\d+)?)\b", r"cos(\1)", text)
    text = re.sub(r"\btan\s+([+-]?\d+(?:\.\d+)?)\b", r"tan(\1)", text)

    # Percentage of: 25% of 480
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)", text
    )
    if match:
        return _clean_number(
            _percent_of(float(match.group(1)), float(match.group(2)))
        )

    # Replace 25% with (25/100)
    text = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", text)

    # ^ means exponentiation for normal calculator users.
    text = text.replace("^", "**")

    # Prevent identifiers/operators outside our controlled AST evaluator.
    if not re.fullmatch(r"[0-9a-zA-Z_+\-*/().,%\s]+", text):
        raise ValueError("Invalid characters")

    tree = ast.parse(text, mode="eval")
    return _clean_number(_evaluate_node(tree))

