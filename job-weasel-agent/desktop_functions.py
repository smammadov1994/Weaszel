"""Desktop automation functions for Weaszel experimental mode."""
import subprocess
import time
from typing import Dict, Any, Optional
from google.genai import types

def open_app(app_name: str) -> Dict[str, Any]:
    """Opens a macOS application by name.
    
    Args:
        app_name: Name of the app to open (e.g., 'Finder', 'Safari', 'Notes')
    
    Returns:
        Status dict with app name and result
    """
    try:
        # Use AppleScript to force activate, which is more reliable for focus
        script = f'tell application "{app_name}" to activate'
        subprocess.run(['osascript', '-e', script], check=True)
        time.sleep(2)  # Give app time to open and focus
        return {"status": "success", "app_name": app_name, "message": f"Opened and activated {app_name}"}
    except subprocess.CalledProcessError:
        # Fallback to open -a if AppleScript fails (e.g. app name mismatch)
        try:
            subprocess.run(['open', '-a', app_name], check=True)
            time.sleep(2)
            return {"status": "success", "app_name": app_name, "message": f"Opened {app_name} (fallback)"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "app_name": app_name, "error": str(e)}

def execute_applescript(script: str) -> Dict[str, Any]:
    """Executes an AppleScript command.
    
    Args:
        script: AppleScript code to execute
    
    Returns:
        Status dict with output or error
    """
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}

def get_desktop_functions():
    """Returns list of desktop function declarations for Gemini."""
    return [
        types.FunctionDeclaration(
            name="open_app",
            description="Opens a macOS application by name (e.g., 'Finder', 'Safari', 'Notes', 'Calculator')",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "app_name": types.Schema(
                        type=types.Type.STRING,
                        description="Name of the macOS application to open"
                    )
                },
                required=["app_name"]
            )
        ),
        types.FunctionDeclaration(
            name="execute_applescript",
            description="Executes an AppleScript command for advanced macOS automation",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "script": types.Schema(
                        type=types.Type.STRING,
                        description="AppleScript code to execute"
                    )
                },
                required=["script"]
            )
        ),
    ]

# Map function names to callable functions
DESKTOP_FUNCTION_MAP = {
    "open_app": open_app,
    "execute_applescript": execute_applescript,
}
