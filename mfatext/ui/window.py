"""Main editor window.

This module provides the main text editor window UI component.
"""

import logging
from pathlib import Path
from typing import Optional

from gi.repository import Adw, Gio, GLib, GObject, Gdk, Gtk

# Try to import GtkSourceView
try:
    import gi
    gi.require_version('GtkSource', '5')
    from gi.repository import GtkSource
    _HAS_GTKSOURCE = True
except (ImportError, ValueError, AttributeError):
    _HAS_GTKSOURCE = False
    GtkSource = None

from mfatext.core.buffer import EditorBuffer
from mfatext.core.search import SearchContext
from mfatext.ui.dialogs import show_unsaved_changes_dialog, show_error_dialog
from mfatext.ui.menus import create_window_menu

logger = logging.getLogger(__name__)


class MfaTextWindow(Adw.Window):
    """Main text editor window.
    
    This window provides a complete text editing interface with syntax
    highlighting, search/replace, undo/redo, and file management.
    """
    
    def __init__(self, application: Adw.Application, file_path: Optional[Path] = None) -> None:
        """Initialize the text editor window.
        
        Args:
            application: The application instance
            file_path: Optional path to a file to open
        """
        super().__init__(application=application)
        self.set_default_size(900, 600)
        self.set_title("MfaText")
        
        self._application = application
        self._editor_buffer: Optional[EditorBuffer] = None
        self._search_context: Optional[SearchContext] = None
        self._is_closing = False
        
        # UI components
        self._source_view: Optional[Gtk.TextView] = None
        self._title_label: Optional[Gtk.Label] = None
        self._save_button: Optional[Gtk.Button] = None
        self._undo_button: Optional[Gtk.Button] = None
        self._redo_button: Optional[Gtk.Button] = None
        self._search_entry: Optional[Gtk.Entry] = None
        self._replace_entry: Optional[Gtk.Entry] = None
        self._search_toolbar: Optional[Gtk.Box] = None
        self._toast_overlay: Optional[Adw.ToastOverlay] = None
        self._current_toast: Optional[Adw.Toast] = None
        
        # Set up UI
        self._setup_ui()
        
        # Set up actions
        self._setup_actions()
        
        # Load file if provided
        if file_path:
            logger.debug(f"__init__: opening file {file_path}")
            self.open_file(file_path)
        else:
            # Create empty buffer
            logger.debug("__init__: creating new empty buffer")
            self._editor_buffer = EditorBuffer()
            self._source_view.set_buffer(self._editor_buffer.buffer)
            self._search_context = SearchContext(self._editor_buffer.buffer)
            logger.debug(f"__init__: buffer type = {type(self._editor_buffer.buffer)}")
            
            # Connect buffer signals
            self._editor_buffer.buffer.connect("modified-changed", self._on_buffer_modified_changed)
            # Connect to text changes to update undo/redo buttons
            self._editor_buffer.buffer.connect("insert-text", self._on_text_changed)
            self._editor_buffer.buffer.connect("delete-range", self._on_text_changed)
            logger.debug("__init__: connected insert-text and delete-range signals")
            if _HAS_GTKSOURCE and isinstance(self._editor_buffer.buffer, GtkSource.Buffer):
                logger.debug("__init__: buffer is GtkSource.Buffer, connecting notify signals")
                self._editor_buffer.buffer.connect("notify::can-undo", self._on_undo_state_changed)
                self._editor_buffer.buffer.connect("notify::can-redo", self._on_redo_state_changed)
                logger.debug("__init__: connected notify::can-undo and notify::can-redo signals")
            else:
                logger.debug(f"__init__: buffer is NOT GtkSource.Buffer. type={type(self._editor_buffer.buffer)}, _HAS_GTKSOURCE={_HAS_GTKSOURCE}")
            
            # Update button states initially
            logger.debug("__init__: scheduling initial state update")
            GLib.idle_add(self._update_undo_redo_states)
            
            self._update_title()
    
    def _setup_ui(self) -> None:
        """Set up the editor UI following GNOME HIG."""
        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)
        
        # Header bar
        header_bar = Adw.HeaderBar()
        self._title_label = Gtk.Label(label="MfaText")
        header_bar.set_title_widget(self._title_label)
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(create_window_menu())
        header_bar.pack_end(menu_button)
        
        # Save button
        self._save_button = Gtk.Button(label="Save")
        self._save_button.add_css_class("suggested-action")
        self._save_button.set_sensitive(False)
        self._save_button.connect("clicked", self._on_save_clicked)
        header_bar.pack_end(self._save_button)
        
        # Undo/Redo buttons
        self._undo_button = Gtk.Button.new_from_icon_name("edit-undo-symbolic")
        self._undo_button.set_tooltip_text("Undo")
        self._undo_button.set_sensitive(False)
        self._undo_button.connect("clicked", self._on_undo_clicked)
        header_bar.pack_start(self._undo_button)
        
        self._redo_button = Gtk.Button.new_from_icon_name("edit-redo-symbolic")
        self._redo_button.set_tooltip_text("Redo")
        self._redo_button.set_sensitive(False)
        self._redo_button.connect("clicked", self._on_redo_clicked)
        header_bar.pack_start(self._redo_button)
        
        # Search button
        search_button = Gtk.Button.new_from_icon_name("system-search-symbolic")
        search_button.set_tooltip_text("Search")
        search_button.connect("clicked", self._on_search_button_clicked)
        header_bar.pack_start(search_button)
        
        toolbar_view.add_top_bar(header_bar)
        
        # Search/replace toolbar
        self._search_toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self._search_toolbar.set_margin_start(6)
        self._search_toolbar.set_margin_end(6)
        self._search_toolbar.set_margin_top(6)
        self._search_toolbar.set_margin_bottom(6)
        
        # Search section
        search_label = Gtk.Label(label="Search:")
        self._search_entry = Gtk.Entry()
        self._search_entry.set_placeholder_text("Search...")
        self._search_entry.set_width_chars(20)
        
        search_prev_btn = Gtk.Button(label="Previous")
        search_prev_btn.connect("clicked", self._on_search_prev_clicked)
        
        search_next_btn = Gtk.Button(label="Next")
        search_next_btn.connect("clicked", self._on_search_next_clicked)
        
        # Replace section
        replace_label = Gtk.Label(label="Replace:")
        self._replace_entry = Gtk.Entry()
        self._replace_entry.set_placeholder_text("Replace with...")
        self._replace_entry.set_width_chars(20)
        
        replace_btn = Gtk.Button(label="Replace")
        replace_btn.connect("clicked", self._on_replace_clicked)
        
        replace_all_btn = Gtk.Button(label="Replace All")
        replace_all_btn.connect("clicked", self._on_replace_all_clicked)
        
        # Pack toolbar
        self._search_toolbar.append(search_label)
        self._search_toolbar.append(self._search_entry)
        self._search_toolbar.append(search_prev_btn)
        self._search_toolbar.append(search_next_btn)
        self._search_toolbar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self._search_toolbar.append(replace_label)
        self._search_toolbar.append(self._replace_entry)
        self._search_toolbar.append(replace_btn)
        self._search_toolbar.append(replace_all_btn)
        
        # Connect search entry signals
        self._search_entry.connect("changed", self._on_search_changed)
        self._search_entry.connect("activate", self._on_search_activate)
        
        # Editor area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        # Create editor widget according to GtkSourceView 5 API
        # Reference: https://gnome.pages.gitlab.gnome.org/gtksourceview/gtksourceview5/class.View.html
        if _HAS_GTKSOURCE:
            # Official API: View() constructor
            self._source_view = GtkSource.View()
            # Official API methods for View configuration
            self._source_view.set_show_line_numbers(True)
            self._source_view.set_highlight_current_line(False)
            self._source_view.set_auto_indent(True)
            self._source_view.set_indent_width(4)
            self._source_view.set_tab_width(4)
            self._source_view.set_insert_spaces_instead_of_tabs(False)
            self._source_view.set_monospace(True)
            self._source_view.set_wrap_mode(Gtk.WrapMode.WORD)
        else:
            self._source_view = Gtk.TextView()
            self._source_view.set_monospace(True)
            self._source_view.set_wrap_mode(Gtk.WrapMode.WORD)
        
        scrolled.set_child(self._source_view)
        
        # Content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.append(self._search_toolbar)
        content_box.append(scrolled)
        
        # Hide search toolbar by default
        self._search_toolbar.set_visible(False)
        
        # Toast overlay
        self._toast_overlay = Adw.ToastOverlay()
        self._toast_overlay.set_child(content_box)
        
        toolbar_view.set_content(self._toast_overlay)
        
        # Keyboard shortcuts
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)
        
        # Apply toast CSS
        self._apply_toast_css()
        
        # Connect close request
        self.connect("close-request", self._on_close_request)
    
    def _setup_actions(self) -> None:
        """Set up window actions."""
        # Create action group for window actions
        action_group = Gio.SimpleActionGroup()
        
        # File actions
        action = Gio.SimpleAction.new("new", None)
        action.connect("activate", lambda *_: self._on_new_file())
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new("open", None)
        action.connect("activate", lambda *_: self._on_open_file())
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new("save", None)
        action.connect("activate", lambda *_: self._on_save_clicked(None))
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new("save-as", None)
        action.connect("activate", lambda *_: self._on_save_as())
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new("close", None)
        action.connect("activate", lambda *_: self._check_and_close())
        action_group.add_action(action)
        
        # Edit actions
        action = Gio.SimpleAction.new("undo", None)
        action.connect("activate", lambda *_: self._on_undo_clicked(None))
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new("redo", None)
        action.connect("activate", lambda *_: self._on_redo_clicked(None))
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new("find", None)
        action.connect("activate", lambda *_: self._on_search_button_clicked(None))
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new("find-replace", None)
        action.connect("activate", lambda *_: self._show_search_toolbar())
        action_group.add_action(action)
        
        # View actions
        action = Gio.SimpleAction.new_stateful("word-wrap", None, GLib.Variant.new_boolean(True))
        action.connect("activate", self._on_word_wrap_toggled)
        action_group.add_action(action)
        
        action = Gio.SimpleAction.new_stateful("line-numbers", None, GLib.Variant.new_boolean(True))
        action.connect("activate", self._on_line_numbers_toggled)
        action_group.add_action(action)
        
        # Insert action group into window
        self.insert_action_group("win", action_group)
    
    def _apply_toast_css(self) -> None:
        """Apply toast CSS styling."""
        try:
            css_provider = Gtk.CssProvider()
            toast_css = """
            toast {
                background-color: alpha(black, 0.6);
                border-radius: 99px;
                color: white;
                font-weight: 500;
                font-size: 1.05em;
                padding: 8px 20px;
                margin: 10px;
                border: 1px solid alpha(white, 0.1);
                box-shadow: 0 5px 15px alpha(black, 0.2);
            }
            toast label {
                color: white;
                font-weight: 500;
            }
            """
            css_provider.load_from_data(toast_css.encode())
            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
                )
        except Exception as e:
            logger.debug(f"Failed to apply toast CSS: {e}")
    
    def _show_toast(self, text: str, timeout: int = 3) -> None:
        """Show a toast message."""
        try:
            if self._current_toast:
                self._current_toast.dismiss()
                self._current_toast = None
            
            toast = Adw.Toast.new(text)
            if timeout >= 0:
                toast.set_timeout(timeout)
            self._toast_overlay.add_toast(toast)
            self._current_toast = toast
        except (AttributeError, RuntimeError, GLib.GError):
            pass
    
    def open_file(self, file_path: Path) -> None:
        """Open a file in the editor.
        
        Args:
            file_path: Path to the file to open
        """
        try:
            self._editor_buffer = EditorBuffer(file_path)
            self._source_view.set_buffer(self._editor_buffer.buffer)
            self._search_context = SearchContext(self._editor_buffer.buffer)
            
            # Connect buffer signals
            self._editor_buffer.buffer.connect("modified-changed", self._on_buffer_modified_changed)
            # Connect to text changes to update undo/redo buttons
            self._editor_buffer.buffer.connect("insert-text", self._on_text_changed)
            self._editor_buffer.buffer.connect("delete-range", self._on_text_changed)
            if _HAS_GTKSOURCE and isinstance(self._editor_buffer.buffer, GtkSource.Buffer):
                self._editor_buffer.buffer.connect("notify::can-undo", self._on_undo_state_changed)
                self._editor_buffer.buffer.connect("notify::can-redo", self._on_redo_state_changed)
            
            # Update button states initially
            GLib.idle_add(self._update_undo_redo_states)
            
            self._update_title()
            self._show_toast("File loaded", timeout=2)
        except Exception as e:
            logger.error(f"Failed to open file: {e}", exc_info=True)
            show_error_dialog(self, f"Failed to open file: {e}")
    
    def _on_new_file(self) -> None:
        """Handle new file action."""
        if self._editor_buffer and self._editor_buffer.is_modified:
            def callback(response: str) -> None:
                if response == "save":
                    self._on_save_clicked(None)
                    GLib.timeout_add(500, self._create_new_file)
                elif response == "discard":
                    self._create_new_file()
            
            show_unsaved_changes_dialog(self, "Untitled", callback)
        else:
            self._create_new_file()
    
    def _create_new_file(self) -> None:
        """Create a new empty file."""
        self._editor_buffer = EditorBuffer()
        self._source_view.set_buffer(self._editor_buffer.buffer)
        self._search_context = SearchContext(self._editor_buffer.buffer)
        
        # Connect buffer signals
        self._editor_buffer.buffer.connect("modified-changed", self._on_buffer_modified_changed)
        # Connect to text changes to update undo/redo buttons
        self._editor_buffer.buffer.connect("insert-text", self._on_text_changed)
        self._editor_buffer.buffer.connect("delete-range", self._on_text_changed)
        logger.debug("_create_new_file: connected insert-text and delete-range signals")
        if _HAS_GTKSOURCE and isinstance(self._editor_buffer.buffer, GtkSource.Buffer):
            logger.debug("_create_new_file: buffer is GtkSource.Buffer, connecting notify signals")
            self._editor_buffer.buffer.connect("notify::can-undo", self._on_undo_state_changed)
            self._editor_buffer.buffer.connect("notify::can-redo", self._on_redo_state_changed)
            logger.debug("_create_new_file: connected notify::can-undo and notify::can-redo signals")
        else:
            logger.debug(f"_create_new_file: buffer is NOT GtkSource.Buffer. type={type(self._editor_buffer.buffer)}, _HAS_GTKSOURCE={_HAS_GTKSOURCE}")
        
        # Update button states initially
        logger.debug("_create_new_file: scheduling initial state update")
        GLib.idle_add(self._update_undo_redo_states)
        
        self._update_title()
    
    def _on_open_file(self) -> None:
        """Handle open file action."""
        if self._editor_buffer and self._editor_buffer.is_modified:
            def callback(response: str) -> None:
                if response == "save":
                    self._on_save_clicked(None)
                    GLib.timeout_add(500, self._show_open_dialog)
                elif response == "discard":
                    self._show_open_dialog()
            
            filename = self._editor_buffer.file_path.name if self._editor_buffer.file_path else "Untitled"
            show_unsaved_changes_dialog(self, filename, callback)
        else:
            self._show_open_dialog()
    
    def _show_open_dialog(self) -> None:
        """Show file open dialog."""
        dialog = Gtk.FileDialog()
        dialog.set_title("Open File")
        dialog.open(self, None, self._on_file_dialog_response)
    
    def _on_file_dialog_response(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        """Handle file dialog response."""
        try:
            file = dialog.open_finish(result)
            if file:
                path = Path(file.get_path())
                self.open_file(path)
        except Exception as e:
            logger.debug(f"File dialog cancelled or error: {e}")
    
    def _on_save_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Handle save button click."""
        if not self._editor_buffer:
            return
        
        if not self._editor_buffer.file_path:
            self._on_save_as()
            return
        
        try:
            self._editor_buffer.save_file()
            self._show_toast("File saved", timeout=2)
            self._update_title()
        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
            show_error_dialog(self, f"Failed to save file: {e}")
    
    def _on_save_as(self) -> None:
        """Handle save as action."""
        dialog = Gtk.FileDialog()
        dialog.set_title("Save File As")
        dialog.set_accept_label("Save")
        dialog.save(self, None, self._on_save_dialog_response)
    
    def _on_save_dialog_response(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        """Handle save dialog response."""
        try:
            file = dialog.save_finish(result)
            if file and self._editor_buffer:
                path = Path(file.get_path())
                self._editor_buffer.save_file(path)
                self._show_toast("File saved", timeout=2)
                self._update_title()
        except Exception as e:
            logger.debug(f"Save dialog cancelled or error: {e}")
    
    def _update_title(self) -> None:
        """Update the window title."""
        if not self._editor_buffer:
            self._title_label.set_label("MfaText")
            return
        
        if self._editor_buffer.file_path:
            filename = self._editor_buffer.file_path.name
            modified = "* " if self._editor_buffer.is_modified else ""
            self._title_label.set_label(f"{modified}{filename}")
            self.set_title(f"{modified}{filename} - MfaText")
        else:
            modified = "* " if self._editor_buffer.is_modified else ""
            self._title_label.set_label(f"{modified}Untitled")
            self.set_title(f"{modified}Untitled - MfaText")
    
    def _on_buffer_modified_changed(self, buffer: Gtk.TextBuffer) -> None:
        """Handle buffer modification state changes."""
        modified = buffer.get_modified()
        self._save_button.set_sensitive(modified)
        self._update_title()
    
    def _on_text_changed(self, *args) -> None:
        """Handle text changes to update undo/redo button states."""
        logger.debug(f"_on_text_changed: called with {len(args)} args")
        # Use idle_add to update after the change is processed
        GLib.idle_add(self._update_undo_redo_states)
    
    def _on_undo_state_changed(self, buffer: GtkSource.Buffer, pspec: GObject.ParamSpec) -> None:
        """Handle undo state changes.
        
        According to GtkSourceView 5 API, can-undo is a property.
        Reference: https://gnome.pages.gitlab.gnome.org/gtksourceview/gtksourceview5/class.Buffer.html
        """
        logger.debug(f"_on_undo_state_changed: called, pspec.name = {pspec.name if pspec else 'None'}")
        if hasattr(self, '_undo_button'):
            logger.debug("_on_undo_state_changed: undo button exists")
            try:
                if isinstance(buffer, GtkSource.Buffer):
                    # Use get_property for can-undo (GtkSourceView 5 API)
                    can_undo = buffer.get_property('can-undo')
                    logger.debug(f"_on_undo_state_changed: get_property('can-undo') = {can_undo}")
                    self._undo_button.set_sensitive(can_undo)
                    logger.debug(f"_on_undo_state_changed: undo button sensitive set to {can_undo}")
                else:
                    logger.debug(f"_on_undo_state_changed: buffer is not GtkSource.Buffer. type={type(buffer)}")
            except Exception as e:
                logger.error(f"_on_undo_state_changed: exception: {e}", exc_info=True)
        else:
            logger.debug("_on_undo_state_changed: undo button does not exist")
    
    def _on_redo_state_changed(self, buffer: GtkSource.Buffer, pspec: GObject.ParamSpec) -> None:
        """Handle redo state changes.
        
        According to GtkSourceView 5 API, can-redo is a property.
        Reference: https://gnome.pages.gitlab.gnome.org/gtksourceview/gtksourceview5/class.Buffer.html
        """
        logger.debug(f"_on_redo_state_changed: called, pspec.name = {pspec.name if pspec else 'None'}")
        if hasattr(self, '_redo_button'):
            logger.debug("_on_redo_state_changed: redo button exists")
            try:
                if isinstance(buffer, GtkSource.Buffer):
                    # Use get_property for can-redo (GtkSourceView 5 API)
                    can_redo = buffer.get_property('can-redo')
                    logger.debug(f"_on_redo_state_changed: get_property('can-redo') = {can_redo}")
                    self._redo_button.set_sensitive(can_redo)
                    logger.debug(f"_on_redo_state_changed: redo button sensitive set to {can_redo}")
                else:
                    logger.debug(f"_on_redo_state_changed: buffer is not GtkSource.Buffer. type={type(buffer)}")
            except Exception as e:
                logger.error(f"_on_redo_state_changed: exception: {e}", exc_info=True)
        else:
            logger.debug("_on_redo_state_changed: redo button does not exist")
    
    def _on_undo_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Handle undo button click."""
        logger.debug("_on_undo_clicked: called")
        if self._editor_buffer:
            logger.debug("_on_undo_clicked: calling editor_buffer.undo()")
            self._editor_buffer.undo()
            # Update button states after undo (use idle_add to ensure state is updated)
            GLib.idle_add(self._update_undo_redo_states)
            logger.debug("_on_undo_clicked: scheduled state update")
        else:
            logger.debug("_on_undo_clicked: no editor buffer")
    
    def _on_redo_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Handle redo button click."""
        logger.debug("_on_redo_clicked: called")
        if self._editor_buffer:
            logger.debug("_on_redo_clicked: calling editor_buffer.redo()")
            self._editor_buffer.redo()
            # Update button states after redo (use idle_add to ensure state is updated)
            GLib.idle_add(self._update_undo_redo_states)
            logger.debug("_on_redo_clicked: scheduled state update")
        else:
            logger.debug("_on_redo_clicked: no editor buffer")
    
    def _update_undo_redo_states(self) -> None:
        """Update undo/redo button states.
        
        According to GtkSourceView 5 API, can-undo and can-redo are properties.
        Reference: https://gnome.pages.gitlab.gnome.org/gtksourceview/gtksourceview5/class.Buffer.html
        """
        logger.debug("_update_undo_redo_states: called")
        if not self._editor_buffer:
            logger.debug("_update_undo_redo_states: no editor buffer")
            return
        
        buffer = self._editor_buffer.buffer
        logger.debug(f"_update_undo_redo_states: buffer type = {type(buffer)}")
        logger.debug(f"_update_undo_redo_states: _HAS_GTKSOURCE = {_HAS_GTKSOURCE}")
        
        if _HAS_GTKSOURCE and isinstance(buffer, GtkSource.Buffer):
            logger.debug("_update_undo_redo_states: buffer is GtkSource.Buffer")
            try:
                # Use get_property for can-undo (GtkSourceView 5 API)
                can_undo = buffer.get_property('can-undo')
                logger.debug(f"_update_undo_redo_states: get_property('can-undo') = {can_undo}")
                self._undo_button.set_sensitive(can_undo)
                logger.debug(f"_update_undo_redo_states: undo button sensitive set to {can_undo}")
                
                # Use get_property for can-redo (GtkSourceView 5 API)
                can_redo = buffer.get_property('can-redo')
                logger.debug(f"_update_undo_redo_states: get_property('can-redo') = {can_redo}")
                self._redo_button.set_sensitive(can_redo)
                logger.debug(f"_update_undo_redo_states: redo button sensitive set to {can_redo}")
            except Exception as e:
                logger.error(f"_update_undo_redo_states: exception: {e}", exc_info=True)
        else:
            logger.debug("_update_undo_redo_states: buffer is NOT GtkSource.Buffer or GtkSource not available")
    
    def _on_search_button_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Toggle search bar visibility."""
        self._show_search_toolbar()
    
    def _show_search_toolbar(self) -> None:
        """Show and focus search toolbar."""
        visible = self._search_toolbar.get_visible()
        self._search_toolbar.set_visible(not visible)
        if not visible and self._search_entry:
            self._search_entry.grab_focus()
    
    def _on_search_changed(self, _editable: Gtk.Editable) -> None:
        """Handle search entry text change."""
        if self._search_context and self._search_entry:
            text = self._search_entry.get_text()
            self._search_context.set_search_text(text)
    
    def _update_search_settings(self) -> None:
        """Update search settings from search entry."""
        if self._search_context and self._search_entry:
            text = self._search_entry.get_text()
            self._search_context.set_search_text(text)
    
    def _on_search_activate(self, _entry: Gtk.Entry) -> None:
        """Handle Enter key in search entry."""
        self._on_search_changed(None)
        self._on_search_next_clicked(None)
    
    def _on_search_next_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Handle search next button click."""
        if not self._search_context or not self._editor_buffer:
            return
        
        # Update search settings before searching
        self._update_search_settings()
        
        # Check if search text is empty
        if not self._search_entry or not self._search_entry.get_text():
            return
        
        ok, match_start, match_end, wrapped = self._search_context.find_next()
        if ok and match_start and match_end:
            self._editor_buffer.buffer.select_range(match_start, match_end)
            # Move cursor to the end of the match so next search starts from after it
            insert_mark = self._editor_buffer.buffer.get_insert()
            self._editor_buffer.buffer.move_mark(insert_mark, match_end)
            self._source_view.scroll_to_iter(match_start, 0.1, True, 0.0, 0.0)
            if wrapped:
                self._show_toast("Search wrapped", timeout=1)
    
    def _on_search_prev_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Handle search previous button click."""
        if not self._search_context or not self._editor_buffer:
            return
        
        ok, match_start, match_end, wrapped = self._search_context.find_previous()
        if ok and match_start and match_end:
            self._editor_buffer.buffer.select_range(match_start, match_end)
            self._source_view.scroll_to_iter(match_start, 0.1, True, 0.0, 0.0)
            if wrapped:
                self._show_toast("Search wrapped", timeout=1)
    
    def _on_replace_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Replace current match and move to next."""
        if not self._search_context or not self._editor_buffer or not self._replace_entry:
            return
        
        # Update search settings before replacing
        self._update_search_settings()
        
        # Check if search text is empty
        if not self._search_entry or not self._search_entry.get_text():
            return
        
        replace_text = self._replace_entry.get_text()
        buffer = self._editor_buffer.buffer
        
        # Check if there's a selection that might be a match
        try:
            has_selection, sel_start, sel_end = buffer.get_selection_bounds()
        except (ValueError, TypeError):
            has_selection = False
            sel_start = None
            sel_end = None
        
        # Get starting position for search
        if has_selection and sel_start is not None:
            # Start from the beginning of the selection
            search_start = sel_start.copy()
        else:
            # Start from cursor position
            insert_mark = buffer.get_insert()
            search_start = buffer.get_iter_at_mark(insert_mark)
        
        # Find the match using the search context
        # According to GtkSource docs, replace() requires iterators from a valid search match
        ok, match_start, match_end, wrapped = self._search_context.find_next(search_start)
        
        if not ok:
            # No match found
            return
        
        # Replace the match using the iterators from the search context
        # replace() requires: match_start, match_end, replace_text, replace_length
        # According to docs, after replace(), the iterators are revalidated to point to the replaced text
        ok = self._search_context.replace(match_start, match_end, replace_text)
        if not ok:
            # Replace failed - the iterators might not correspond to a valid match
            return
        
        # After replace(), match_start and match_end iterators are revalidated to point to the replaced text
        # Select the replaced text and scroll to it
        buffer.select_range(match_start, match_end)
        self._source_view.scroll_to_iter(match_start, 0.1, True, 0.0, 0.0)
        
        # Move to next occurrence automatically
        # The iterators now point to the replaced text, so we can search from the end
        self._on_search_next_clicked(None)
    
    def _on_replace_all_clicked(self, _button: Optional[Gtk.Button]) -> None:
        """Replace all matches."""
        if not self._search_context or not self._replace_entry:
            return
        
        # Update search settings before replacing
        self._update_search_settings()
        
        # Check if search text is empty
        if not self._search_entry or not self._search_entry.get_text():
            return
        
        replace_text = self._replace_entry.get_text()
        if not replace_text:
            return
        
        # replace_all() needs the replace text and its length (in characters)
        self._search_context.replace_all(replace_text)
        self._show_toast("Replace all completed", timeout=2)
    
    def _on_word_wrap_toggled(self, action: Gio.SimpleAction, _variant: GLib.Variant) -> None:
        """Handle word wrap toggle."""
        state = action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(not state))
        wrap_mode = Gtk.WrapMode.WORD if not state else Gtk.WrapMode.NONE
        self._source_view.set_wrap_mode(wrap_mode)
    
    def _on_line_numbers_toggled(self, action: Gio.SimpleAction, _variant: GLib.Variant) -> None:
        """Handle line numbers toggle."""
        state = action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(not state))
        if _HAS_GTKSOURCE and isinstance(self._source_view, GtkSource.View):
            self._source_view.set_show_line_numbers(not state)
    
    def _on_key_pressed(
        self,
        controller: Gtk.EventControllerKey,
        keyval: int,
        keycode: int,
        state: Gdk.ModifierType,
    ) -> bool:
        """Handle keyboard shortcuts."""
        ctrl = state & Gdk.ModifierType.CONTROL_MASK
        shift = state & Gdk.ModifierType.SHIFT_MASK
        
        # Ctrl+F -> show search
        if ctrl and keyval == Gdk.KEY_f:
            self._show_search_toolbar()
            return True
        
        # Ctrl+H -> show search with replace
        if ctrl and keyval == Gdk.KEY_h:
            self._show_search_toolbar()
            if self._replace_entry:
                self._replace_entry.grab_focus()
            return True
        
        # Ctrl+Z -> undo
        if ctrl and keyval == Gdk.KEY_z and not shift:
            logger.debug("_on_key_pressed: Ctrl+Z detected")
            if self._editor_buffer:
                logger.debug("_on_key_pressed: calling editor_buffer.undo()")
                self._editor_buffer.undo()
                GLib.idle_add(self._update_undo_redo_states)
                logger.debug("_on_key_pressed: scheduled state update after undo")
                return True
            else:
                logger.debug("_on_key_pressed: no editor buffer for undo")
        
        # Ctrl+Shift+Z or Ctrl+Y -> redo
        if (ctrl and shift and keyval == Gdk.KEY_z) or (ctrl and keyval == Gdk.KEY_y):
            logger.debug("_on_key_pressed: Ctrl+Shift+Z or Ctrl+Y detected")
            if self._editor_buffer:
                logger.debug("_on_key_pressed: calling editor_buffer.redo()")
                self._editor_buffer.redo()
                GLib.idle_add(self._update_undo_redo_states)
                logger.debug("_on_key_pressed: scheduled state update after redo")
                return True
            else:
                logger.debug("_on_key_pressed: no editor buffer for redo")
        
        return False
    
    def _on_close_request(self, _window: Adw.Window) -> bool:
        """Handle window close request."""
        self._check_and_close()
        return True
    
    def _check_and_close(self) -> None:
        """Check for unsaved changes and close if okay."""
        if self._editor_buffer and self._editor_buffer.is_modified:
            filename = self._editor_buffer.file_path.name if self._editor_buffer.file_path else "Untitled"
            
            def callback(response: str) -> None:
                if response == "save":
                    self._on_save_clicked(None)
                    GLib.timeout_add(500, self._do_close)
                elif response == "discard":
                    self._do_close()
            
            show_unsaved_changes_dialog(self, filename, callback)
        else:
            self._do_close()
    
    def _do_close(self) -> None:
        """Actually close the window and clean up."""
        self._is_closing = True
        if self._editor_buffer:
            self._editor_buffer.cleanup()
        self.destroy()

