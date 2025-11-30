"""Dialog windows for the text editor.

This module provides various dialogs following GNOME HIG guidelines.
"""

from typing import Callable
from gi.repository import Adw, Gtk, Gdk


def show_about_dialog(parent: Adw.Window) -> None:
    """Show the about dialog following GNOME HIG.
    
    According to LibAdwaita 1.7 API:
    https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1.7/class.AboutDialog.html
    
    Args:
        parent: Parent window for the dialog
    """
    # Use Adw.AboutDialog (available since LibAdwaita 1.5)
    # Reference: https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1.7/class.AboutDialog.html
    about = Adw.AboutDialog()
    
    # Set application properties according to official API
    about.set_application_name("MfaText")
    about.set_application_icon("text-editor")  # Using text-editor icon until mfatext icon is available
    about.set_version("1.0.0")
    about.set_developer_name("MfaText Contributors")
    about.set_license_type(Gtk.License.GPL_3_0)
    about.set_website("https://github.com/mfatext/mfatext")
    about.set_issue_url("https://github.com/mfatext/mfatext/issues")
    about.set_copyright("© 2024 MfaText Contributors")
    about.set_developers(["MfaText Contributors"])
    about.set_artists(["GNOME Design Team"])
    about.set_comments("A feature-rich text editor for GNOME")
    
    # Present the dialog (AboutDialog is a Dialog, not a Window)
    about.present(parent)


def show_help_dialog(parent: Adw.Window) -> None:
    """Show the help dialog.
    
    Args:
        parent: Parent window for the dialog
    """
    help_text = """<big><b>MfaText Help</b></big>

<b>Keyboard Shortcuts:</b>

• <b>Ctrl+N</b> - New file
• <b>Ctrl+O</b> - Open file
• <b>Ctrl+S</b> - Save file
• <b>Ctrl+Shift+S</b> - Save As
• <b>Ctrl+W</b> - Close window
• <b>Ctrl+Q</b> - Quit application
• <b>Ctrl+F</b> - Find
• <b>Ctrl+H</b> - Find and Replace
• <b>Ctrl+Z</b> - Undo
• <b>Ctrl+Shift+Z</b> or <b>Ctrl+Y</b> - Redo
• <b>Ctrl+A</b> - Select All
• <b>Ctrl+C</b> - Copy
• <b>Ctrl+V</b> - Paste
• <b>Ctrl+X</b> - Cut

<b>Features:</b>

• Syntax highlighting for many programming languages
• Search and replace functionality
• Undo/redo support
• Line numbers
• Word wrap
• Auto-indentation
• File monitoring for external changes

For more information, visit the project website.
"""
    
    dialog = Adw.AlertDialog.new("Help", help_text)
    dialog.add_response("close", "Close")
    dialog.set_default_response("close")
    dialog.set_close_response("close")
    dialog.present(parent)


def show_unsaved_changes_dialog(
    parent: Adw.Window,
    filename: str,
    callback: Callable[[str], None],
) -> None:
    """Show dialog for unsaved changes.
    
    Args:
        parent: Parent window
        filename: Name of the file with unsaved changes
        callback: Function to call with response ("save", "discard", or "cancel")
    """
    dialog = Adw.AlertDialog.new(
        "Unsaved Changes",
        f"You have unsaved changes to {filename}. Save changes before closing?"
    )
    dialog.add_response("cancel", "Cancel")
    dialog.add_response("discard", "Discard Changes")
    dialog.add_response("save", "Save")
    dialog.set_default_response("save")
    dialog.set_close_response("cancel")
    
    def on_response(_dialog: Adw.AlertDialog, response: str) -> None:
        callback(response)
    
    dialog.connect("response", on_response)
    dialog.present(parent)


def show_error_dialog(parent: Adw.Window, message: str) -> None:
    """Show an error dialog.
    
    Args:
        parent: Parent window
        message: Error message to display
    """
    dialog = Adw.AlertDialog.new("Error", message)
    dialog.add_response("ok", "OK")
    dialog.set_default_response("ok")
    dialog.set_close_response("ok")
    dialog.present(parent)

