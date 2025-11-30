"""Setup script for the text editor package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="mfatext",
    version="1.0.0",
    description="A feature-rich text editor for GNOME",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MfaText Contributors",
    author_email="mfatext@example.com",
    url="https://github.com/mfatext/mfatext",
    license="GPL-3.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PyGObject>=3.42.0",
    ],
    extras_require={
        "syntax": [
            "gtksourceview5",
        ],
    },
    entry_points={
        "console_scripts": [
            "mfatext=mfatext.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Editors",
    ],
    data_files=[
        ("share/applications", ["data/com.github.mfatext.MfaText.desktop"]),
        ("share/metainfo", ["data/com.github.mfatext.MfaText.metainfo.xml"]),
    ],
)

