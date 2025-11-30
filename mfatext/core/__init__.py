"""Core editor functionality.

This module contains the core logic for the text editor, separated from
the UI components.
"""

from mfatext.core.buffer import EditorBuffer
from mfatext.core.search import SearchContext

__all__ = ["EditorBuffer", "SearchContext"]

