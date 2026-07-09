# backend/app/tools/python_exec.py

import sys
import io
import contextlib
from app.tools.base import BaseTool

class PythonExecutionTool:
    """Executes Python code in a restricted environment and captures stdout."""
    name = "python_exec"
    description = "Useful for executing Python code. Input should be valid Python code. Prints will be captured and returned."

    async def run(self, input_data: str) -> str:
        # Restricted builtins to prevent malicious code execution
        safe_builtins = {
            "print": print, "len": len, "range": range, "str": str, 
            "int": int, "float": float, "list": list, "dict": dict, 
            "sum": sum, "max": max, "min": min, "abs": abs, "round": round,
            "True": True, "False": False, "None": None
        }
        
        # Capture stdout
        stdout_capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_capture):
                exec(input_data, {"__builtins__": safe_builtins}, {})
            
            output = stdout_capture.getvalue()
            return output if output else "Code executed successfully with no output."
        except Exception as e:
            return f"Execution error: {str(e)}"