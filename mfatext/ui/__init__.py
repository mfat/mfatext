"""UI components for the text editor."""

from mfatext.ui.window import MfaTextWindow
from mfatext.ui.menus import create_app_menu, create_window_menu
from mfatext.ui.dialogs import show_about_dialog, show_help_dialog

__all__ = [
    "MfaTextWindow",
    "create_app_menu",
    "create_window_menu",
    "show_about_dialog",
    "show_help_dialog",
]

