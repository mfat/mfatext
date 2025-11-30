# Function Reference

This document provides a comprehensive reference for all functions and methods in the text editor codebase.

## Table of Contents

- [Application Module](#application-module)
- [Core Modules](#core-modules)
  - [Buffer](#buffer)
  - [Search](#search)
- [UI Modules](#ui-modules)
  - [Window](#window)
  - [Menus](#menus)
  - [Dialogs](#dialogs)
- [Utility Modules](#utility-modules)
  - [XDG Utilities](#xdg-utilities)
  - [File Operations](#file-operations)

---

## Application Module

### `texteditor.application.TextEditorApplication`

Main application class that can be used both as a standalone application and as a library module.

#### `__init__(application_id: str = "com.github.texteditor.TextEditor")`

Initialize the application.

**Parameters:**
- `application_id` (str): Application ID following reverse DNS notation

**Returns:** None

#### `_setup_actions() -> None`

Set up application actions (help, about, quit).

**Returns:** None

#### `_on_activate(app: Adw.Application) -> None`

Handle application activation. Creates a new window.

**Parameters:**
- `app` (Adw.Application): The application instance

**Returns:** None

#### `_on_open(app: Adw.Application, files: list[Gio.File], n_files: int, hint: str) -> None`

Handle file opening from command line or file manager.

**Parameters:**
- `app` (Adw.Application): The application instance
- `files` (list[Gio.File]): List of files to open
- `n_files` (int): Number of files
- `hint` (str): Hint string

**Returns:** None

#### `_on_help(_action: Gio.SimpleAction, _parameter: GLib.Variant) -> None`

Handle help action. Shows the help dialog.

**Parameters:**
- `_action` (Gio.SimpleAction): The action
- `_parameter` (GLib.Variant): Action parameter

**Returns:** None

#### `_on_about(_action: Gio.SimpleAction, _parameter: GLib.Variant) -> None`

Handle about action. Shows the about dialog.

**Parameters:**
- `_action` (Gio.SimpleAction): The action
- `_parameter` (GLib.Variant): Action parameter

**Returns:** None

#### `_on_quit(_action: Gio.SimpleAction, _parameter: GLib.Variant) -> None`

Handle quit action. Quits the application.

**Parameters:**
- `_action` (Gio.SimpleAction): The action
- `_parameter` (GLib.Variant): Action parameter

**Returns:** None

#### `create_window(file_path: Optional[Path] = None) -> MfaTextWindow`

Create a new editor window. This method allows the application to be used as a library.

**Parameters:**
- `file_path` (Optional[Path]): Optional path to a file to open

**Returns:**
- `MfaTextWindow`: New MfaTextWindow instance

#### `main() -> int`

Main entry point for the standalone application.

**Returns:**
- `int`: Exit code

---

## Core Modules

### Buffer

#### `mfatext.core.buffer.EditorBuffer`

Manages the editor buffer and file operations.

#### `__init__(file_path: Optional[Path] = None) -> None`

Initialize the editor buffer.

**Parameters:**
- `file_path` (Optional[Path]): Optional path to the file to edit

**Returns:** None

#### `buffer() -> Gtk.TextBuffer`

Get the underlying GTK text buffer.

**Returns:**
- `Gtk.TextBuffer`: The text buffer

#### `file_path() -> Optional[Path]`

Get the current file path.

**Returns:**
- `Optional[Path]`: Current file path or None

#### `is_modified() -> bool`

Check if the buffer has been modified.

**Returns:**
- `bool`: True if modified, False otherwise

#### `load_file(file_path: Path) -> None`

Load a file into the buffer.

**Parameters:**
- `file_path` (Path): Path to the file to load

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `IOError`: If the file cannot be read

**Returns:** None

#### `save_file(file_path: Optional[Path] = None, encoding: str = 'utf-8') -> None`

Save the buffer content to a file.

**Parameters:**
- `file_path` (Optional[Path]): Optional path to save to (uses current path if not provided)
- `encoding` (str): Encoding to use (default: 'utf-8')

**Raises:**
- `ValueError`: If no file path is available
- `IOError`: If the file cannot be written

**Returns:** None

#### `can_undo() -> bool`

Check if undo is available.

**Returns:**
- `bool`: True if undo is available

#### `can_redo() -> bool`

Check if redo is available.

**Returns:**
- `bool`: True if redo is available

#### `undo() -> None`

Undo the last action.

**Returns:** None

#### `redo() -> None`

Redo the last undone action.

**Returns:** None

#### `cleanup() -> None`

Clean up resources (file monitoring, etc.).

**Returns:** None

### Search

#### `mfatext.core.search.SearchContext`

Manages search and replace operations.

#### `__init__(buffer: Gtk.TextBuffer) -> None`

Initialize the search context.

**Parameters:**
- `buffer` (Gtk.TextBuffer): The text buffer to search in

**Returns:** None

#### `set_search_text(text: str, case_sensitive: bool = False, wrap_around: bool = True) -> None`

Set the search text.

**Parameters:**
- `text` (str): Text to search for
- `case_sensitive` (bool): Whether search should be case sensitive (default: False)
- `wrap_around` (bool): Whether to wrap around when reaching end/beginning (default: True)

**Returns:** None

#### `find_next(start_iter: Optional[Gtk.TextIter] = None) -> tuple[bool, Optional[Gtk.TextIter], Optional[Gtk.TextIter], bool]`

Find the next occurrence of the search text.

**Parameters:**
- `start_iter` (Optional[Gtk.TextIter]): Optional iterator to start search from (uses cursor if None)

**Returns:**
- `tuple[bool, Optional[Gtk.TextIter], Optional[Gtk.TextIter], bool]`: Tuple of (found, match_start, match_end, wrapped)

#### `find_previous(start_iter: Optional[Gtk.TextIter] = None) -> tuple[bool, Optional[Gtk.TextIter], Optional[Gtk.TextIter], bool]`

Find the previous occurrence of the search text.

**Parameters:**
- `start_iter` (Optional[Gtk.TextIter]): Optional iterator to start search from (uses cursor if None)

**Returns:**
- `tuple[bool, Optional[Gtk.TextIter], Optional[Gtk.TextIter], bool]`: Tuple of (found, match_start, match_end, wrapped)

#### `replace(match_start: Gtk.TextIter, match_end: Gtk.TextIter, replace_text: str) -> bool`

Replace a match with new text.

**Parameters:**
- `match_start` (Gtk.TextIter): Iterator at start of match
- `match_end` (Gtk.TextIter): Iterator at end of match
- `replace_text` (str): Text to replace with

**Returns:**
- `bool`: True if replacement was successful

#### `replace_all(replace_text: str) -> None`

Replace all occurrences of the search text.

**Parameters:**
- `replace_text` (str): Text to replace with

**Returns:** None

---

## UI Modules

### Window

#### `mfatext.ui.window.MfaTextWindow`

Main text editor window.

#### `__init__(application: Adw.Application, file_path: Optional[Path] = None) -> None`

Initialize the text editor window.

**Parameters:**
- `application` (Adw.Application): The application instance
- `file_path` (Optional[Path]): Optional path to a file to open

**Returns:** None

#### `open_file(file_path: Path) -> None`

Open a file in the editor.

**Parameters:**
- `file_path` (Path): Path to the file to open

**Returns:** None

### Menus

#### `mfatext.ui.menus.create_app_menu() -> Gio.Menu`

Create the application menu following GNOME HIG.

**Returns:**
- `Gio.Menu`: Menu with application menu items

#### `mfatext.ui.menus.create_window_menu() -> Gio.Menu`

Create the window menu following GNOME HIG.

**Returns:**
- `Gio.Menu`: Menu with window menu items

### Dialogs

#### `mfatext.ui.dialogs.show_about_dialog(parent: Adw.Window) -> None`

Show the about dialog following GNOME HIG.

**Parameters:**
- `parent` (Adw.Window): Parent window for the dialog

**Returns:** None

#### `mfatext.ui.dialogs.show_help_dialog(parent: Adw.Window) -> None`

Show the help dialog.

**Parameters:**
- `parent` (Adw.Window): Parent window for the dialog

**Returns:** None

#### `mfatext.ui.dialogs.show_unsaved_changes_dialog(parent: Adw.Window, filename: str, callback: callable) -> None`

Show dialog for unsaved changes.

**Parameters:**
- `parent` (Adw.Window): Parent window
- `filename` (str): Name of the file with unsaved changes
- `callback` (callable): Function to call with response ("save", "discard", or "cancel")

**Returns:** None

#### `mfatext.ui.dialogs.show_error_dialog(parent: Adw.Window, message: str) -> None`

Show an error dialog.

**Parameters:**
- `parent` (Adw.Window): Parent window
- `message` (str): Error message to display

**Returns:** None

---

## Utility Modules

### XDG Utilities

#### `mfatext.utils.xdg.get_user_data_dir(app_name: str = "mfatext") -> Path`

Get the user data directory following XDG standards.

**Parameters:**
- `app_name` (str): Application name for the subdirectory (default: "mfatext")

**Returns:**
- `Path`: Path to the user data directory

#### `mfatext.utils.xdg.get_user_config_dir(app_name: str = "mfatext") -> Path`

Get the user config directory following XDG standards.

**Parameters:**
- `app_name` (str): Application name for the subdirectory (default: "mfatext")

**Returns:**
- `Path`: Path to the user config directory

#### `mfatext.utils.xdg.get_user_cache_dir(app_name: str = "mfatext") -> Path`

Get the user cache directory following XDG standards.

**Parameters:**
- `app_name` (str): Application name for the subdirectory (default: "mfatext")

**Returns:**
- `Path`: Path to the user cache directory

#### `mfatext.utils.xdg.ensure_directories_exist(app_name: str = "mfatext") -> None`

Ensure all XDG directories exist for the application.

**Parameters:**
- `app_name` (str): Application name for the subdirectories (default: "texteditor")

**Returns:** None

### File Operations

#### `mfatext.utils.file_ops.detect_encoding(file_path: Path) -> Tuple[str, bytes]`

Detect the encoding of a file.

**Parameters:**
- `file_path` (Path): Path to the file to detect encoding for

**Returns:**
- `Tuple[str, bytes]`: Tuple of (encoding_name, file_content_bytes)

#### `mfatext.utils.file_ops.load_file(file_path: Path) -> str`

Load a text file with automatic encoding detection.

**Parameters:**
- `file_path` (Path): Path to the file to load

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `IOError`: If the file cannot be read

**Returns:**
- `str`: File contents as a string

#### `mfatext.utils.file_ops.save_file(file_path: Path, content: str, encoding: str = 'utf-8') -> None`

Save text content to a file.

**Parameters:**
- `file_path` (Path): Path where to save the file
- `content` (str): Text content to save
- `encoding` (str): Encoding to use (default: 'utf-8')

**Raises:**
- `IOError`: If the file cannot be written

**Returns:** None

---

## Notes

- All UI components follow GNOME HIG (Human Interface Guidelines)
- File operations use XDG Base Directory Standard
- The application can be used both as a standalone app and as a library module
- All methods are documented with type hints for better IDE support

