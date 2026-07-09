# backend/app/tools/calculator.py

import ast
import operator
from app.tools.base import BaseTool

# Safe operators for AST evaluation
SAFE_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.BitXor: operator.xor,
    ast.USub: operator.neg
}

def _eval_expr(node):
    """Recursively evaluates an AST node safely."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        return SAFE_OPS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    elif isinstance(node, ast.UnaryOp):
        return SAFE_OPS[type(node.op)](_eval_expr(node.operand))
    else:
        raise ValueError(f"Unsupported expression type: {type(node)}")

class CalculatorTool:
    """Safely evaluates mathematical expressions."""
    name = "calculator"
    description = "Useful for performing mathematical calculations. Input must be a valid math expression (e.g., '2 + 2 * 5')."

    async def run(self, input_data: str) -> str:
        try:
            # Parse the expression into an AST
            node = ast.parse(input_data.strip(), mode='eval')
            result = _eval_expr(node.body)
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"