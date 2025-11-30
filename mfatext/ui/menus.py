"""Menu creation for the text editor.

This module provides functions to create application and window menus
following GNOME HIG guidelines.
"""

from gi.repository import Gio, GLib


def create_app_menu() -> Gio.Menu:
    """Create the application menu following GNOME HIG.
    
    Returns:
        Gio.Menu with application menu items
    """
    menu = Gio.Menu()
    
    # Help section
    help_section = Gio.Menu()
    help_section.append("Help", "app.help")
    help_section.append("About", "app.about")
    
    menu.append_section(None, help_section)
    
    return menu


def create_window_menu() -> Gio.Menu:
    """Create the window menu following GNOME HIG.
    
    Returns:
        Gio.Menu with window menu items
    """
    menu = Gio.Menu()
    
    # File section
    file_section = Gio.Menu()
    file_section.append("New", "win.new")
    file_section.append("Open", "win.open")
    file_section.append("Save", "win.save")
    file_section.append("Save As…", "win.save-as")
    file_section.append("Close", "win.close")
    
    # Edit section
    edit_section = Gio.Menu()
    edit_section.append("Undo", "win.undo")
    edit_section.append("Redo", "win.redo")
    edit_section.append("Find", "win.find")
    edit_section.append("Find and Replace", "win.find-replace")
    
    # View section
    view_section = Gio.Menu()
    view_section.append("Word Wrap", "win.word-wrap")
    view_section.append("Line Numbers", "win.line-numbers")
    
    # Help section (includes About)
    help_section = Gio.Menu()
    help_section.append("Help", "app.help")
    help_section.append("About", "app.about")
    
    menu.append_section(None, file_section)
    menu.append_section(None, edit_section)
    menu.append_section(None, view_section)
    menu.append_section(None, help_section)
    
    return menu

