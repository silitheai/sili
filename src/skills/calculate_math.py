import math
import operator

def calculate_math(expression: str) -> str:
    """Safely evaluates a mathematical expression string."""
    # List of allowed math functions/constants
    allowed_names = {
        'abs': abs, 'round': round,
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10,
        'pi': math.pi, 'e': math.e,
        'pow': math.pow, 'factorial': math.factorial
    }
    
    try:
        # Use eval securely by removing builtins and only allowing math components
        code = compile(expression, "<string>", "eval")
        for names in code.co_names:
            if names not in allowed_names:
                raise NameError(f"Use of '{names}' is not allowed in math calculation.")
                
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating math expression: {str(e)}"
