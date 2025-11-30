"""Search and replace functionality.

This module provides search and replace functionality for the text editor.
"""

import logging
from typing import Optional

from gi.repository import Gtk, GtkSource

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


class SearchContext:
    """Manages search and replace operations.
    
    This class handles search settings, finding matches, and replacing text.
    """
    
    def __init__(self, buffer: Gtk.TextBuffer) -> None:
        """Initialize the search context.
        
        Args:
            buffer: The text buffer to search in
        """
        self._buffer = buffer
        
        if _HAS_GTKSOURCE and isinstance(buffer, GtkSource.Buffer):
            self._search_settings = GtkSource.SearchSettings()
            self._search_context = GtkSource.SearchContext.new(buffer, self._search_settings)
            self._search_context.set_highlight(True)
        else:
            self._search_settings = None
            self._search_context = None
    
    def set_search_text(self, text: str, case_sensitive: bool = False, wrap_around: bool = True) -> None:
        """Set the search text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether search should be case sensitive
            wrap_around: Whether to wrap around when reaching end/beginning
        """
        if not _HAS_GTKSOURCE or not self._search_settings:
            return
        
        if text:
            self._search_settings.set_search_text(text)
        else:
            self._search_settings.set_search_text(None)
        
        self._search_settings.set_case_sensitive(case_sensitive)
        self._search_settings.set_wrap_around(wrap_around)
    
    def find_next(self, start_iter: Optional[Gtk.TextIter] = None) -> tuple[bool, Optional[Gtk.TextIter], Optional[Gtk.TextIter], bool]:
        """Find the next occurrence of the search text.
        
        Args:
            start_iter: Optional iterator to start search from (uses cursor if None)
            
        Returns:
            Tuple of (found, match_start, match_end, wrapped) where:
            - found: True if a match was found
            - match_start: Iterator at start of match (or None)
            - match_end: Iterator at end of match (or None)
            - wrapped: True if search wrapped around
        """
        if not _HAS_GTKSOURCE or not self._search_context:
            return (False, None, None, False)
        
        if start_iter is None:
            # Use cursor position or selection end
            try:
                has_selection, sel_start, sel_end = self._buffer.get_selection_bounds()
                if has_selection:
                    start_iter = sel_end.copy()
                    if not start_iter.is_end():
                        start_iter.forward_char()
                else:
                    insert_mark = self._buffer.get_insert()
                    start_iter = self._buffer.get_iter_at_mark(insert_mark)
            except (ValueError, TypeError):
                insert_mark = self._buffer.get_insert()
                start_iter = self._buffer.get_iter_at_mark(insert_mark)
        
        ok, match_start, match_end, wrapped = self._search_context.forward(start_iter)
        return (ok, match_start, match_end, wrapped)
    
    def find_previous(self, start_iter: Optional[Gtk.TextIter] = None) -> tuple[bool, Optional[Gtk.TextIter], Optional[Gtk.TextIter], bool]:
        """Find the previous occurrence of the search text.
        
        Args:
            start_iter: Optional iterator to start search from (uses cursor if None)
            
        Returns:
            Tuple of (found, match_start, match_end, wrapped) where:
            - found: True if a match was found
            - match_start: Iterator at start of match (or None)
            - match_end: Iterator at end of match (or None)
            - wrapped: True if search wrapped around
        """
        if not _HAS_GTKSOURCE or not self._search_context:
            return (False, None, None, False)
        
        if start_iter is None:
            insert_mark = self._buffer.get_insert()
            start_iter = self._buffer.get_iter_at_mark(insert_mark)
        
        ok, match_start, match_end, wrapped = self._search_context.backward(start_iter)
        return (ok, match_start, match_end, wrapped)
    
    def replace(self, match_start: Gtk.TextIter, match_end: Gtk.TextIter, replace_text: str) -> bool:
        """Replace a match with new text.
        
        Args:
            match_start: Iterator at start of match
            match_end: Iterator at end of match
            replace_text: Text to replace with
            
        Returns:
            True if replacement was successful
        """
        if not _HAS_GTKSOURCE or not self._search_context:
            return False
        
        return self._search_context.replace(match_start, match_end, replace_text, len(replace_text))
    
    def replace_all(self, replace_text: str) -> None:
        """Replace all occurrences of the search text.
        
        Args:
            replace_text: Text to replace with
        """
        if not _HAS_GTKSOURCE or not self._search_context:
            return
        
        self._search_context.replace_all(replace_text, len(replace_text))

