import math
import re

def calculate(text):
    text = text.strip().lower()

    text = text.replace("^", "**")
    text = text.replace("×", "*")
    text = text.replace("÷", "/")

    # Handle "25% of 480"
    m = re.match(r"(\d+(\.\d+)?)%\s+of\s+(\d+(\.\d+)?)", text)
    if m:
        percent = float(m.group(1))
        number = float(m.group(3))
        return (percent / 100) * number

    allowed = {
        "__builtins__": {},
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
        "pow": pow,
    }

    return eval(text, allowed)
