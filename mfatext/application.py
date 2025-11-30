"""Main application class.

This module provides the main application class that can be used both
as a standalone application and as a library module.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import gi
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio, GLib

from mfatext.ui.window import MfaTextWindow
from mfatext.ui.menus import create_app_menu
from mfatext.ui.dialogs import show_about_dialog, show_help_dialog
from mfatext.utils.xdg import ensure_directories_exist

logger = logging.getLogger(__name__)


class MfaTextApplication(Adw.Application):
    """Main text editor application.
    
    This class can be used both as a standalone application and as a
    library module for integration into other PyGObject applications.
    """
    
    def __init__(self, application_id: str = "com.github.mfatext.MfaText") -> None:
        """Initialize the application.
        
        Args:
            application_id: Application ID following reverse DNS notation
        """
        super().__init__(
            application_id=application_id,
            flags=Gio.ApplicationFlags.HANDLES_OPEN
        )
        
        self._windows = []
        
        # Ensure XDG directories exist
        ensure_directories_exist("mfatext")
        
        # Set up actions
        self._setup_actions()
        
        # Connect signals
        self.connect("activate", self._on_activate)
        self.connect("open", self._on_open)
    
    def _setup_actions(self) -> None:
        """Set up application actions."""
        # Help action
        action = Gio.SimpleAction.new("help", None)
        action.connect("activate", self._on_help)
        self.add_action(action)
        
        # About action
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self._on_about)
        self.add_action(action)
        
        # Quit action
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self._on_quit)
        self.add_action(action)
        
        # Set up application menu (after registration)
        # We'll set this in _on_activate after app is registered
    
    def _on_activate(self, app: Adw.Application) -> None:
        """Handle application activation."""
        # Set up application menu now that app is registered
        if not self.get_menubar():
            self.set_menubar(create_app_menu())
        
        # Create a new window
        window = MfaTextWindow(app)
        window.present()
        self._windows.append(window)
    
    def _on_open(self, app: Adw.Application, files: list[Gio.File], n_files: int, hint: str) -> None:
        """Handle file opening."""
        for file in files:
            path = Path(file.get_path())
            window = MfaTextWindow(app, path)
            window.present()
            self._windows.append(window)
    
    def _on_help(self, _action: Gio.SimpleAction, _parameter: GLib.Variant) -> None:
        """Handle help action."""
        if self._windows:
            show_help_dialog(self._windows[0])
    
    def _on_about(self, _action: Gio.SimpleAction, _parameter: GLib.Variant) -> None:
        """Handle about action."""
        if self._windows:
            show_about_dialog(self._windows[0])
    
    def _on_quit(self, _action: Gio.SimpleAction, _parameter: GLib.Variant) -> None:
        """Handle quit action."""
        self.quit()
    
    def create_window(self, file_path: Optional[Path] = None) -> MfaTextWindow:
        """Create a new editor window.
        
        This method allows the application to be used as a library.
        
        Args:
            file_path: Optional path to a file to open
            
        Returns:
            New MfaTextWindow instance
        """
        window = MfaTextWindow(self, file_path)
        self._windows.append(window)
        return window


def main() -> int:
    """Main entry point for the standalone application.
    
    Returns:
        Exit code
    """
    # Set up logging with DEBUG level for detailed debugging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run application
    app = MfaTextApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())

