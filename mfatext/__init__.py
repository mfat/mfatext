"""A feature-rich text editor for GNOME.

This package provides a text editor that can be used both as a standalone
application and as a library module for integration into PyGObject applications.
"""

__version__ = "1.0.0"
__author__ = "MfaText Contributors"

from mfatext.application import MfaTextApplication
from mfatext.ui.window import MfaTextWindow

__all__ = ["MfaTextApplication", "MfaTextWindow"]

