# MfaText

A feature-rich text editor for GNOME that can be used both as a standalone application and as a library module for integration into PyGObject applications.

## Features

- **Syntax Highlighting**: Support for many programming languages via GtkSourceView
- **Search and Replace**: Full-featured search and replace functionality
- **Undo/Redo**: Complete undo/redo support
- **Line Numbers**: Optional line number display
- **Word Wrap**: Configurable word wrapping
- **Auto-indentation**: Automatic indentation support
- **File Monitoring**: Detects external file changes
- **GNOME Integration**: Follows GNOME HIG guidelines
- **XDG Standards**: Uses freedesktop.org XDG Base Directory Specification

## Installation

### From Source

```bash
git clone https://github.com/mfatext/mfatext.git
cd mfatext
pip install .
```

### Using Requirements Files

Alternatively, you can install dependencies using requirements files:

```bash
# Install runtime dependencies (includes GtkSourceView 5 for syntax highlighting)
pip install -r requirements.txt

# Install for development (includes all dependencies and build tools)
pip install -r requirements-dev.txt
```

### As a Library

The text editor can be used as a library in your PyGObject applications:

```python
from pathlib import Path
from mfatext import MfaTextApplication, MfaTextWindow

# Create application
app = MfaTextApplication()

# Create a window
window = app.create_window(file_path=Path("example.txt"))
window.present()
```

For detailed integration instructions and examples, see the [Integration Guide](docs/INTEGRATION_GUIDE.md).

## Usage

### Standalone Application

Run the text editor from the command line:

```bash
mfatext [file1] [file2] ...
```

Or open files from the file manager.

### Keyboard Shortcuts

- **Ctrl+N** - New file
- **Ctrl+O** - Open file
- **Ctrl+S** - Save file
- **Ctrl+Shift+S** - Save As
- **Ctrl+W** - Close window
- **Ctrl+Q** - Quit application
- **Ctrl+F** - Find
- **Ctrl+H** - Find and Replace
- **Ctrl+Z** - Undo
- **Ctrl+Shift+Z** or **Ctrl+Y** - Redo
- **Ctrl+A** - Select All
- **Ctrl+C** - Copy
- **Ctrl+V** - Paste
- **Ctrl+X** - Cut

## Packaging

The text editor can be packaged for various distributions:

### Flatpak

```bash
cd flatpak
flatpak-builder build com.github.mfatext.MfaText.yml
flatpak-builder --user --install build com.github.mfatext.MfaText.yml
```

### Debian Package

```bash
dpkg-buildpackage -b
```

### RPM Package

```bash
rpmbuild -ba mfatext.spec
```

### Arch Linux Package

```bash
makepkg -si
```

## Development

### Requirements

**System Dependencies:**
- Python 3.8+
- GTK 4 development libraries
- LibAdwaita development libraries
- GtkSourceView 5 development libraries
- PyGObject and introspection bindings

**Python Dependencies:**

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Or manually:
- PyGObject 3.42.0+
- gtksourceview5 (required - provides the text editor component)

### Project Structure

```
mfatext/
├── mfatext/          # Main package
│   ├── core/           # Core editor logic
│   │   ├── buffer.py   # Buffer management
│   │   └── search.py   # Search/replace
│   ├── ui/             # UI components
│   │   ├── window.py   # Main window
│   │   ├── menus.py    # Menu creation
│   │   └── dialogs.py  # Dialog windows
│   ├── utils/          # Utilities
│   │   ├── xdg.py      # XDG utilities
│   │   └── file_ops.py # File operations
│   ├── application.py  # Application class
│   └── main.py         # Entry point
├── data/               # Desktop files and metadata
├── flatpak/            # Flatpak packaging
├── debian/             # Debian packaging
└── setup.py            # Python package setup
```

### Code Organization

The codebase is organized into logical modules:

- **Core**: Business logic separated from UI
- **UI**: User interface components
- **Utils**: Utility functions and helpers

This separation makes the code easy to read, expand, maintain, package, and redistribute.

## Documentation

- [Integration Guide](docs/INTEGRATION_GUIDE.md) - Complete guide for using MfaText in your application
- [Function Reference](docs/function_reference.md) - Complete API documentation

## License

GPL-3.0

## Contributing

Contributions are welcome! Please follow the existing code style and ensure all functions are documented.

