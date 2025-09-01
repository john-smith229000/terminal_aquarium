import sys
import os

class CrossPlatformInput:
    """
    Cross-platform non-blocking keyboard input handler.
    Provides a unified interface for getting keyboard input across different operating systems.
    """
    
    def __init__(self):
        self.platform = sys.platform
        self._setup_platform_specific()
    
    def _setup_platform_specific(self):
        """Initialize platform-specific modules and settings."""
        if self.platform == "win32":
            try:
                import msvcrt
                self.msvcrt = msvcrt
                self.input_method = 'windows'
            except ImportError:
                print("Warning: msvcrt not available on Windows. Falling back to basic input.")
                self.input_method = 'fallback'
        else:
            # Unix-like systems (Linux, macOS)
            try:
                import tty
                import termios
                import select
                import signal
                
                self.tty = tty
                self.termios = termios
                self.select = select
                self.signal = signal
                self.input_method = 'unix'
                
                # Store original terminal settings to restore later
                self.fd = sys.stdin.fileno()
                self.original_settings = None
                
                # Set up signal handler for cleanup
                signal.signal(signal.SIGINT, self._cleanup_handler)
                signal.signal(signal.SIGTERM, self._cleanup_handler)
                
            except ImportError as e:
                print(f"Warning: Unix terminal modules not available: {e}")
                print("Falling back to basic input method.")
                self.input_method = 'fallback'
    
    def _cleanup_handler(self, signum, frame):
        """Signal handler to ensure terminal is restored on exit."""
        self.cleanup()
        sys.exit(0)
    
    def setup_raw_mode(self):
        """Set up raw mode for Unix terminals."""
        if self.input_method == 'unix':
            try:
                self.original_settings = self.termios.tcgetattr(self.fd)
                self.tty.setraw(self.fd)
            except Exception as e:
                print(f"Warning: Could not set raw mode: {e}")
                self.input_method = 'fallback'
    
    def cleanup(self):
        """Restore terminal settings."""
        if self.input_method == 'unix' and self.original_settings:
            try:
                self.termios.tcsetattr(self.fd, self.termios.TCSADRAIN, self.original_settings)
            except Exception:
                pass  # Best effort cleanup
    
    def get_char(self):
        """
        Get a single character from input without blocking.
        Returns None if no input is available, or the character/special key name.
        """
        if self.input_method == 'windows':
            return self._get_char_windows()
        elif self.input_method == 'unix':
            return self._get_char_unix()
        else:
            return self._get_char_fallback()
    
    def _get_char_windows(self):
        """Windows-specific non-blocking character input."""
        if self.msvcrt.kbhit():
            try:
                char = self.msvcrt.getch()
                
                # Handle special keys
                if char == b'\x1b':  # ESC
                    return 'ESC'
                elif char == b'\x03':  # Ctrl+C
                    return 'CTRL_C'
                elif char == b'\r':   # Enter (Windows uses \r)
                    return 'ENTER'
                elif char == b'\x08': # Backspace
                    return 'BACKSPACE'
                
                # Handle extended keys (arrow keys, function keys, etc.)
                if char == b'\x00' or char == b'\xe0':
                    # Read the second byte for extended keys
                    extended = self.msvcrt.getch()
                    # You can add specific extended key handling here if needed
                    return f'EXTENDED_{ord(extended)}'
                
                # Regular character
                return char.decode('utf-8', errors='ignore')
                
            except (UnicodeDecodeError, ValueError):
                return None
        return None
    
    def _get_char_unix(self):
        """Unix-specific non-blocking character input."""
        try:
            # Check if there's input available
            if self.select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                char = sys.stdin.read(1)
                
                # Handle special characters
                if not char:  # EOF
                    return 'EOF'
                elif ord(char) == 27:  # ESC
                    # Check for escape sequences (arrow keys, etc.)
                    if self.select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                        seq = sys.stdin.read(2)
                        if seq == '[A':
                            return 'UP'
                        elif seq == '[B':
                            return 'DOWN'
                        elif seq == '[C':
                            return 'RIGHT'
                        elif seq == '[D':
                            return 'LEFT'
                        # Add more escape sequences as needed
                    return 'ESC'
                elif ord(char) == 3:   # Ctrl+C
                    return 'CTRL_C'
                elif ord(char) == 10 or ord(char) == 13:  # Enter (Unix uses \n)
                    return 'ENTER'
                elif ord(char) == 127: # Backspace/Delete
                    return 'BACKSPACE'
                
                return char
        except Exception:
            return None
        return None
    
    def _get_char_fallback(self):
        """
        Fallback method for systems where platform-specific methods don't work.
        This is blocking input, so it's not ideal but ensures basic functionality.
        """
        try:
            # Use select to check if input is available (Unix-like systems)
            if hasattr(self, 'select'):
                if self.select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                    return sys.stdin.read(1)
            return None
        except Exception:
            return None


def create_input_handler():
    """Factory function to create and initialize the input handler."""
    handler = CrossPlatformInput()
    
    # Set up raw mode for Unix systems
    if handler.input_method == 'unix':
        handler.setup_raw_mode()
    
    return handler