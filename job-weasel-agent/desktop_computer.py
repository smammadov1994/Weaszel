"""Desktop-only computer for executing desktop tasks without a browser."""
from typing import Any, Dict
from computers import Computer, EnvState
import time

class DesktopComputer(Computer):
    """A minimal computer implementation for desktop-only tasks."""
    
    def __init__(self):
        self._screen_size = (1440, 900)  # Default screen size
    
    @property
    def screen_size(self) -> tuple[int, int]:
        """Returns the screen dimensions."""
        return self._screen_size
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def current_state(self) -> EnvState:
        """Returns a minimal state with desktop screenshot."""
        import subprocess
        import tempfile
        import os
        
        try:
            # Use macOS screencapture to take screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Capture entire screen
            subprocess.run(['screencapture', '-x', tmp_path], check=True, capture_output=True)
            
            # Read the screenshot
            with open(tmp_path, 'rb') as f:
                screenshot_bytes = f.read()
            
            # Clean up
            os.unlink(tmp_path)
            
        except Exception as e:
            # Fallback to empty if screenshot fails
            screenshot_bytes = b''
            print(f"Warning: Could not capture desktop screenshot: {e}")
        
        return EnvState(
            screenshot=screenshot_bytes,
            url="desktop://",
            error=None
        )
    
    # Placeholder methods - not used in desktop-only mode
    def open_web_browser(self) -> EnvState:
        return self.current_state()
    
    def click_at(self, x: int, y: int) -> EnvState:
        return self.current_state()
    
    def hover_at(self, x: int, y: int) -> EnvState:
        return self.current_state()
    
    def type_text_at(self, x: int, y: int, text: str, press_enter: bool = False, clear_before_typing: bool = True) -> EnvState:
        return self.current_state()
    
    def scroll_document(self, direction: str) -> EnvState:
        return self.current_state()
    
    def scroll_at(self, x: int, y: int, direction: str, magnitude: int = 800) -> EnvState:
        return self.current_state()
    
    def wait_5_seconds(self) -> EnvState:
        time.sleep(5)
        return self.current_state()
    
    def go_back(self) -> EnvState:
        return self.current_state()
    
    def go_forward(self) -> EnvState:
        return self.current_state()
    
    def search(self) -> EnvState:
        return self.current_state()
    
    def navigate(self, url: str) -> EnvState:
        return self.current_state()
    
    def key_combination(self, keys: list[str]) -> EnvState:
        return self.current_state()
    
    def drag_and_drop(self, x: int, y: int, destination_x: int, destination_y: int) -> EnvState:
        return self.current_state()
