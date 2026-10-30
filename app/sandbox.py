"""Execution Sandbox for QuestLearn: Shadows of the Machine.

Enforces an AST security baseline, execution timeouts (<= 2.0s),
and returns structured execution results and stack traces.
"""
import ast
import sys
import subprocess
import tempfile
import os
from typing import Dict, Any

# Prohibited imports and builtins to prevent host escaping
DISALLOWED_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil", "pty", "commands",
    "posix", "nt", "builtins", "importlib", "pathlib", "ctypes"
}

DISALLOWED_CALLS = {
    "eval", "exec", "__import__", "open", "compile", "breakpoint", "getattr", "setattr"
}


def _verify_ast_safety(code_str: str) -> Dict[str, Any]:
    """Parse AST to detect security hazards or syntax errors."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return {
            "safe": False,
            "error_type": "SyntaxError",
            "error_message": f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}\n  {e.text or ''}"
        }

    for node in ast.walk(tree):
        # Check imports: import os, import sys
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                if root_module in DISALLOWED_MODULES:
                    return {
                        "safe": False,
                        "error_type": "SecurityViolation",
                        "error_message": (
                            f"KERNEL FAULT: Unauthorized module import '{root_module}' "
                            f"rejected by AetherOS sandboxed memory partition."
                        )
                    }

        # Check from ... import ...
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split(".")[0]
                if root_module in DISALLOWED_MODULES:
                    return {
                        "safe": False,
                        "error_type": "SecurityViolation",
                        "error_message": (
                            f"KERNEL FAULT: Unauthorized import from '{root_module}' "
                            f"rejected by AetherOS sandboxed memory partition."
                        )
                    }

        # Check dangerous builtin calls: eval(), exec(), open()
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in DISALLOWED_CALLS:
                return {
                    "safe": False,
                    "error_type": "SecurityViolation",
                    "error_message": (
                        f"KERNEL FAULT: Prohibited execution primitive '{node.func.id}()' "
                        f"detected in submitted patch."
                    )
                }

    return {"safe": True}


def execute_user_patch(user_code: str, test_assertions: str) -> Dict[str, Any]:
    """Combines user code with test assertions and runs it in an isolated subprocess.
    
    Enforces a strict 2.0-second execution timeout.
    """
    # 1. AST Security and Syntax Validation
    safety_check = _verify_ast_safety(user_code)
    if not safety_check["safe"]:
        return {
            "success": False,
            "error_type": safety_check["error_type"],
            "error_message": safety_check["error_message"],
            "output": "",
            "returncode": 1
        }

    # 2. Combine candidate code with unit tests
    combined_code = f"{user_code}\n\n# --- TEST HARNESS ---\n{test_assertions}\nprint('ALL_UNIT_TESTS_PASSED_OK')\n"

    # 3. Spawn isolated python subprocess
    # We use -I to run Python in isolated mode (disables -E, -s, user site, ignores PYTHON* env vars)
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", combined_code],
            capture_output=True,
            text=True,
            timeout=2.0
        )

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode

        if returncode == 0 and "ALL_UNIT_TESTS_PASSED_OK" in stdout:
            # Clean up internal token from visible output
            clean_output = stdout.replace("ALL_UNIT_TESTS_PASSED_OK\n", "").replace("ALL_UNIT_TESTS_PASSED_OK", "")
            return {
                "success": True,
                "error_type": None,
                "error_message": "",
                "output": clean_output.strip() or "Kernel memory sector stabilized successfully. All unit tests verified.",
                "returncode": 0
            }
        else:
            # Extract error type from stderr traceback
            error_type = "RuntimeError"
            for line in stderr.splitlines():
                if "Error:" in line or "Exception:" in line:
                    error_type = line.split(":")[0].strip()
                    break

            return {
                "success": False,
                "error_type": error_type,
                "error_message": stderr.strip() or "Assertion failed or non-zero exit status encountered.",
                "output": stdout.strip(),
                "returncode": returncode
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "TimeoutError",
            "error_message": (
                "Execution halted: Infinite execution loop or runaway recursion detected. "
                "Process terminated after exceeding 2.0s kernel timeout."
            ),
            "output": "",
            "returncode": -1
        }
    except Exception as exc:
        return {
            "success": False,
            "error_type": "SubprocessError",
            "error_message": f"Execution environment failure: {str(exc)}",
            "output": "",
            "returncode": -1
        }
