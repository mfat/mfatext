"""Editor buffer management.

This module provides the core buffer management logic for the text editor,
handling file loading, saving, and modification tracking.
"""

import logging
from pathlib import Path
from typing import Optional

from gi.repository import Gtk, Gio, GLib

from mfatext.utils.file_ops import load_file, save_file

logger = logging.getLogger(__name__)

# Try to import GtkSourceView
try:
    import gi
    gi.require_version('GtkSource', '5')
    from gi.repository import GtkSource
    _HAS_GTKSOURCE = True
except (ImportError, ValueError, AttributeError):
    _HAS_GTKSOURCE = False
    GtkSource = None


class EditorBuffer:
    """Manages the editor buffer and file operations.
    
    This class handles loading and saving files, tracking modifications,
    and managing the text buffer state.
    """
    
    def __init__(self, file_path: Optional[Path] = None) -> None:
        """Initialize the editor buffer.
        
        Args:
            file_path: Optional path to the file to edit
        """
        self._file_path: Optional[Path] = file_path
        self._file_monitor: Optional[Gio.FileMonitor] = None
        self._file_modified_time: float = 0.0
        self._is_loading = False
        
        # Create buffer
        if _HAS_GTKSOURCE:
            # Detect language from file extension
            language = None
            if file_path:
                language_manager = GtkSource.LanguageManager.get_default()
                language = language_manager.guess_language(file_path.name, None)
            
            if language:
                self._buffer = GtkSource.Buffer.new_with_language(language)
            else:
                self._buffer = GtkSource.Buffer()
        else:
            self._buffer = Gtk.TextBuffer()
        
        # Connect to buffer changes
        self._buffer.connect("modified-changed", self._on_buffer_modified_changed)
        
        # Load file if path provided
        if file_path and file_path.exists():
            self.load_file(file_path)
    
    @property
    def buffer(self) -> Gtk.TextBuffer:
        """Get the underlying GTK text buffer."""
        return self._buffer
    
    @property
    def file_path(self) -> Optional[Path]:
        """Get the current file path."""
        return self._file_path
    
    @property
    def is_modified(self) -> bool:
        """Check if the buffer has been modified."""
        return self._buffer.get_modified()
    
    def load_file(self, file_path: Path) -> None:
        """Load a file into the buffer.
        
        Args:
            file_path: Path to the file to load
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If the file cannot be read
        """
        self._is_loading = True
        try:
            content = load_file(file_path)
            self._buffer.set_text(content)
            self._buffer.set_modified(False)
            self._file_path = file_path
            self._file_modified_time = file_path.stat().st_mtime
            
            # Reset undo/redo state after loading
            if _HAS_GTKSOURCE and isinstance(self._buffer, GtkSource.Buffer):
                try:
                    self._buffer.begin_not_undoable_action()
                    self._buffer.end_not_undoable_action()
                except (AttributeError, TypeError):
                    pass
            
            # Set up file monitoring
            self._setup_file_monitoring()
            
        finally:
            self._is_loading = False
    
    def save_file(self, file_path: Optional[Path] = None, encoding: str = 'utf-8') -> None:
        """Save the buffer content to a file.
        
        Args:
            file_path: Optional path to save to (uses current path if not provided)
            encoding: Encoding to use (default: utf-8)
            
        Raises:
            ValueError: If no file path is available
            IOError: If the file cannot be written
        """
        save_path = file_path or self._file_path
        if not save_path:
            raise ValueError("No file path available for saving")
        
        start, end = self._buffer.get_bounds()
        content = self._buffer.get_text(start, end, False)
        
        save_file(save_path, content, encoding)
        self._buffer.set_modified(False)
        self._file_path = save_path
        self._file_modified_time = save_path.stat().st_mtime
        
        # Reset undo stack after save
        if _HAS_GTKSOURCE and isinstance(self._buffer, GtkSource.Buffer):
            try:
                self._buffer.begin_not_undoable_action()
                self._buffer.end_not_undoable_action()
            except (AttributeError, TypeError):
                pass
    
    def _setup_file_monitoring(self) -> None:
        """Set up file monitoring to detect external changes."""
        if not self._file_path:
            return
        
        try:
            # Cancel existing monitor
            if self._file_monitor:
                self._file_monitor.cancel()
            
            gfile = Gio.File.new_for_path(str(self._file_path))
            self._file_monitor = gfile.monitor_file(Gio.FileMonitorFlags.WATCH_MOVES, None)
            self._file_monitor.connect("changed", self._on_file_changed)
        except Exception as e:
            logger.warning(f"Failed to set up file monitoring: {e}")
    
    def _on_file_changed(
        self,
        monitor: Gio.FileMonitor,
        file: Gio.File,
        other_file: Optional[Gio.File],
        event_type: Gio.FileMonitorEvent,
    ) -> None:
        """Handle file system changes."""
        if not self._file_path or not self._file_path.exists():
            return
        
        # Only care about changes (not moves/deletes)
        if event_type in (Gio.FileMonitorEvent.CHANGED, Gio.FileMonitorEvent.CHANGES_DONE_HINT):
            try:
                new_mtime = self._file_path.stat().st_mtime
                if new_mtime > self._file_modified_time:
                    self._file_modified_time = new_mtime
                    # Emit signal for external reload handling
                    GLib.idle_add(self._on_file_changed_externally)
            except Exception:
                pass
    
    def _on_file_changed_externally(self) -> None:
        """Handle when file is changed externally."""
        # This can be overridden or connected to by UI components
        pass
    
    def _on_buffer_modified_changed(self, buffer: Gtk.TextBuffer) -> None:
        """Handle buffer modification state changes."""
        # Ignore during loading
        if self._is_loading:
            return
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        if _HAS_GTKSOURCE and isinstance(self._buffer, GtkSource.Buffer):
            try:
                # Try get_property first (GtkSource properties)
                return self._buffer.get_property('can-undo')
            except (AttributeError, TypeError):
                try:
                    # Fallback to method call
                    return self._buffer.can_undo()
                except (AttributeError, TypeError):
                    pass
        return False
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        if _HAS_GTKSOURCE and isinstance(self._buffer, GtkSource.Buffer):
            try:
                # Try get_property first (GtkSource properties)
                return self._buffer.get_property('can-redo')
            except (AttributeError, TypeError):
                try:
                    # Fallback to method call
                    return self._buffer.can_redo()
                except (AttributeError, TypeError):
                    pass
        return False
    
    def undo(self) -> None:
        """Undo the last action."""
        if _HAS_GTKSOURCE and isinstance(self._buffer, GtkSource.Buffer):
            try:
                # Check if undo is available
                can_undo = False
                try:
                    can_undo = self._buffer.get_property('can-undo')
                except (AttributeError, TypeError):
                    try:
                        can_undo = self._buffer.can_undo()
                    except (AttributeError, TypeError):
                        pass
                
                if can_undo:
                    self._buffer.undo()
            except (AttributeError, TypeError):
                pass
    
    def redo(self) -> None:
        """Redo the last undone action."""
        if _HAS_GTKSOURCE and isinstance(self._buffer, GtkSource.Buffer):
            try:
                # Check if redo is available
                can_redo = False
                try:
                    can_redo = self._buffer.get_property('can-redo')
                except (AttributeError, TypeError):
                    try:
                        can_redo = self._buffer.can_redo()
                    except (AttributeError, TypeError):
                        pass
                
                if can_redo:
                    self._buffer.redo()
            except (AttributeError, TypeError):
                pass
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self._file_monitor:
            self._file_monitor.cancel()
            self._file_monitor = None

