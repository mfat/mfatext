# Integration Guide: Using MfaText in Your Application

This guide explains how to integrate MfaText into your own PyGObject/GNOME application. MfaText can be used in several ways depending on your needs.

## Installation as a Dependency

First, install MfaText in your application's environment:

```bash
pip install mfatext
```

Or add it to your `requirements.txt` or `pyproject.toml`:

```toml
[project]
dependencies = [
    "mfatext>=1.0.0",
    # ... your other dependencies
]
```

## Basic Usage

### 1. Embedding a Full Editor Window

The simplest way is to create a complete editor window within your application:

```python
from pathlib import Path
from mfatext import MfaTextApplication, MfaTextWindow
from gi.repository import Adw

class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.MyApp")
        self.connect("activate", self.on_activate)
    
    def on_activate(self, app):
        # Create the MfaText application wrapper
        self.text_editor_app = MfaTextApplication()
        
        # Create an editor window (optionally with a file)
        window = self.text_editor_app.create_window(
            file_path=Path("/path/to/file.txt")
        )
        
        # Show the window
        window.present()
        
        # Keep reference to prevent garbage collection
        self.editor_window = window

# Run your application
app = MyApplication()
app.run()
```

### 2. Using Only the Window Component

You can create editor windows directly if you already have an Adw.Application:

```python
from pathlib import Path
from mfatext.ui.window import MfaTextWindow
from gi.repository import Adw

class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.MyApp")
        self.connect("activate", self.on_activate)
    
    def on_activate(self, app):
        # Create editor window directly
        editor_window = MfaTextWindow(
            application=self,
            file_path=Path("/path/to/file.txt")  # Optional
        )
        editor_window.present()

app = MyApplication()
app.run()
```

### 3. Using Core Components Directly

For more control, you can use the core components (buffer, search) and build your own UI:

#### Using the Editor Buffer

```python
from pathlib import Path
from mfatext.core.buffer import EditorBuffer
from gi.repository import Gtk

# Create a buffer
buffer = EditorBuffer(file_path=Path("example.txt"))

# Get the underlying Gtk.TextBuffer or GtkSource.Buffer
gtk_buffer = buffer.buffer()

# Access buffer properties
is_modified = buffer.is_modified()
file_path = buffer.file_path()

# File operations
buffer.save_file()  # Save to current file
buffer.save_file(Path("new_file.txt"))  # Save to new file

# Undo/Redo
if buffer.can_undo():
    buffer.undo()
if buffer.can_redo():
    buffer.redo()

# Clean up when done
buffer.cleanup()
```

#### Using Search Functionality

```python
from mfatext.core.search import SearchContext
from gi.repository import Gtk

# Assume you have a text buffer
buffer = EditorBuffer()
gtk_buffer = buffer.buffer()

# Create search context
search = SearchContext(gtk_buffer)

# Configure search
search.set_search_text(
    text="hello",
    case_sensitive=False,
    wrap_around=True
)

# Find next occurrence
found, start_iter, end_iter, wrapped = search.find_next()
if found:
    # Select the found text
    gtk_buffer.select_range(start_iter, end_iter)
    print(f"Found at position {start_iter.get_offset()}-{end_iter.get_offset()}")

# Find previous
found, start_iter, end_iter, wrapped = search.find_previous()

# Replace current match
if found:
    search.replace(start_iter, end_iter, "hi")

# Replace all occurrences
search.replace_all("hi")
```

## Advanced Usage Examples

### Example 1: Multi-Window Text Editor Application

```python
from pathlib import Path
from mfatext import MfaTextApplication, MfaTextWindow
from gi.repository import Adw, Gio, GLib

class MyMultiWindowApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.example.MultiEditor",
            flags=Gio.ApplicationFlags.HANDLES_OPEN
        )
        self.windows = []
        self.connect("activate", self.on_activate)
        self.connect("open", self.on_open)
    
    def on_activate(self, app):
        # Create new empty window
        self.create_editor_window()
    
    def on_open(self, app, files, n_files, hint):
        # Open files from command line or file manager
        for file in files:
            path = Path(file.get_path())
            self.create_editor_window(file_path=path)
    
    def create_editor_window(self, file_path=None):
        text_app = MfaTextApplication()
        window = text_app.create_window(file_path=file_path)
        window.present()
        self.windows.append(window)

app = MyMultiWindowApp()
app.run()
```

### Example 2: Embedding Editor in a Custom Window

```python
from pathlib import Path
from mfatext.core.buffer import EditorBuffer
from mfatext.core.search import SearchContext
from gi.repository import Adw, Gtk

class CustomEditorWindow(Adw.Window):
    def __init__(self, application, file_path=None):
        super().__init__(application=application)
        self.set_default_size(800, 600)
        
        # Create editor buffer
        self.buffer = EditorBuffer(file_path)
        
        # Create text view with syntax highlighting
        try:
            import gi
            gi.require_version('GtkSource', '5')
            from gi.repository import GtkSource
            self.text_view = GtkSource.View.new_with_buffer(self.buffer.buffer())
            
            # Configure syntax highlighting
            lang_manager = GtkSource.LanguageManager.get_default()
            if file_path:
                lang = lang_manager.guess_language(file_path, None)
                if lang:
                    self.buffer.buffer().set_language(lang)
        except:
            # Fallback to regular text view
            self.text_view = Gtk.TextView.new_with_buffer(self.buffer.buffer())
        
        # Create search context
        self.search_context = SearchContext(self.buffer.buffer())
        
        # Create UI
        self.setup_ui()
    
    def setup_ui(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Add scrollable text view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.text_view)
        box.append(scrolled)
        
        # Add custom toolbar or buttons here
        # ...
        
        self.set_content(box)

class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.CustomEditor")
        self.connect("activate", self.on_activate)
    
    def on_activate(self, app):
        window = CustomEditorWindow(self, Path("example.txt"))
        window.present()

app = MyApp()
app.run()
```

### Example 3: Accessing Window Contents Programmatically

```python
from mfatext.ui.window import MfaTextWindow
from gi.repository import Adw

# After creating a window
window = MfaTextWindow(application, file_path=Path("file.txt"))

# Access the internal buffer (you may need to access private attributes)
# Note: This is accessing private implementation details
# A better approach would be to add public methods to MfaTextWindow

# Get buffer content programmatically
buffer = window._editor_buffer
text = buffer.buffer().get_text(
    buffer.buffer().get_start_iter(),
    buffer.buffer().get_end_iter(),
    False
)

# Save programmatically
buffer.save_file()

# Check if modified
is_modified = buffer.is_modified()
```

## API Reference

### MfaTextApplication

Main application class that manages editor windows.

#### Methods

- `__init__(application_id: str = "com.github.mfatext.MfaText")`
  - Initialize the application
  
- `create_window(file_path: Optional[Path] = None) -> MfaTextWindow`
  - Create a new editor window
  - Parameters:
    - `file_path`: Optional path to a file to open
  - Returns: New MfaTextWindow instance

### MfaTextWindow

Complete text editor window with UI.

#### Methods

- `__init__(application: Adw.Application, file_path: Optional[Path] = None)`
  - Initialize the window
  - Parameters:
    - `application`: The Adw.Application instance
    - `file_path`: Optional path to a file to open

- `open_file(file_path: Path) -> None`
  - Open a file in the editor
  - Parameters:
    - `file_path`: Path to the file to open

### EditorBuffer

Manages the text buffer and file operations.

#### Methods

- `buffer() -> Gtk.TextBuffer`
  - Get the underlying GTK text buffer

- `file_path() -> Optional[Path]`
  - Get the current file path

- `is_modified() -> bool`
  - Check if the buffer has been modified

- `load_file(file_path: Path) -> None`
  - Load a file into the buffer

- `save_file(file_path: Optional[Path] = None, encoding: str = 'utf-8') -> None`
  - Save the buffer to a file

- `can_undo() -> bool` / `can_redo() -> bool`
  - Check undo/redo availability

- `undo() -> None` / `redo() -> None`
  - Perform undo/redo operations

- `cleanup() -> None`
  - Clean up resources

### SearchContext

Manages search and replace operations.

#### Methods

- `set_search_text(text: str, case_sensitive: bool = False, wrap_around: bool = True) -> None`
  - Configure search parameters

- `find_next(start_iter: Optional[Gtk.TextIter] = None) -> tuple`
  - Find next occurrence
  - Returns: (found, match_start, match_end, wrapped)

- `find_previous(start_iter: Optional[Gtk.TextIter] = None) -> tuple`
  - Find previous occurrence

- `replace(match_start: Gtk.TextIter, match_end: Gtk.TextIter, replace_text: str) -> bool`
  - Replace a single match

- `replace_all(replace_text: str) -> None`
  - Replace all occurrences

## Utility Functions

### File Operations

```python
from mfatext.utils.file_ops import load_file, save_file, detect_encoding

# Load file with encoding detection
content = load_file(Path("file.txt"))

# Save file
save_file(Path("output.txt"), "content here", encoding="utf-8")

# Detect encoding
encoding, content_bytes = detect_encoding(Path("file.txt"))
```

### XDG Utilities

```python
from mfatext.utils.xdg import (
    get_user_data_dir,
    get_user_config_dir,
    get_user_cache_dir,
    ensure_directories_exist
)

# Get XDG directories
data_dir = get_user_data_dir("myapp")
config_dir = get_user_config_dir("myapp")
cache_dir = get_user_cache_dir("myapp")

# Ensure directories exist
ensure_directories_exist("myapp")
```

## Integration Patterns

### Pattern 1: Standalone Editor Mode

Use MfaText as a complete standalone editor with minimal setup:

```python
from mfatext import MfaTextApplication

app = MfaTextApplication()
window = app.create_window()
window.present()
app.run()
```

### Pattern 2: Embedded Component

Use only the core components and build custom UI:

```python
from mfatext.core.buffer import EditorBuffer
from mfatext.core.search import SearchContext

# Use buffer and search in your custom UI
buffer = EditorBuffer()
search = SearchContext(buffer.buffer())
```

### Pattern 3: Hybrid Approach

Use MfaText windows alongside your own windows:

```python
# Your custom windows
custom_window = MyCustomWindow()

# MfaText windows
editor_window = MfaTextWindow(application, file_path)

# Both work together in the same application
```

## Requirements

When using MfaText in your application, ensure you have:

- Python 3.8+
- PyGObject 3.42.0+
- GTK 4
- LibAdwaita
- GtkSourceView 5 (optional, for syntax highlighting)

These should be installed as system packages on most GNOME-based distributions, or you can specify them in your packaging configuration.

## Best Practices

1. **Resource Management**: Always clean up buffers when done:
   ```python
   buffer.cleanup()
   ```

2. **Error Handling**: Handle file operations with try/except:
   ```python
   try:
       buffer.load_file(path)
   except (FileNotFoundError, IOError) as e:
       show_error_dialog(window, str(e))
   ```

3. **Unsaved Changes**: Check for unsaved changes before closing:
   ```python
   if buffer.is_modified():
       # Prompt user to save
   ```

4. **Application ID**: Use your own application ID:
   ```python
   app = MfaTextApplication(application_id="com.example.MyApp")
   ```

## Troubleshooting

### Syntax Highlighting Not Working

Ensure GtkSourceView 5 is installed:
```bash
# On Fedora/RHEL
sudo dnf install gtksourceview5-devel

# On Ubuntu/Debian
sudo apt install libgtksourceview-5-dev

# Then install Python bindings
pip install gtksourceview5
```

### Import Errors

Make sure all dependencies are installed:
```bash
pip install PyGObject mfatext
```

### Window Not Showing

Make sure to call `present()` or `show()` on the window:
```python
window.present()  # Preferred for Adw.Window
# or
window.show()     # Alternative
```

## Additional Resources

- See [Function Reference](function_reference.md) for complete API documentation
- See [README](../README.md) for general information about MfaText
- Check the source code in `mfatext/` for implementation details

