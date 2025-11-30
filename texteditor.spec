%global py3ver %(python3 -c "import sys; print(sys.version_info[1])")
%global pyver %(python3 -c "import sys; print('%d.%d' % sys.version_info[:2])")

Name:           mfatext
Version:        1.0.0
Release:        1%{?dist}
Summary:        A feature-rich text editor for GNOME
License:        GPL-3.0
URL:            https://github.com/mfatext/mfatext
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-gobject
BuildRequires:  python3-gobject-base
BuildRequires:  gtk4-devel
BuildRequires:  libadwaita-devel
BuildRequires:  gtksourceview5-devel

Requires:       python3-gobject
Requires:       python3-gobject-base
Requires:       gtk4
Requires:       libadwaita
Requires:       gtksourceview5

%description
MfaText is a feature-rich text editor for GNOME that can be used
both as a standalone application and as a library module for integration
into PyGObject applications.

Features include:
- Syntax highlighting for many programming languages
- Search and replace functionality
- Undo/redo support
- Line numbers
- Word wrap
- Auto-indentation
- File monitoring for external changes

%prep
%autosetup -n %{name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --root=%{buildroot} --optimize=1

%files
%{python3_sitelib}/mfatext
%{_bindir}/mfatext
%{_datadir}/applications/com.github.mfatext.MfaText.desktop
%{_datadir}/metainfo/com.github.mfatext.MfaText.metainfo.xml

%changelog
* Mon Jan 01 2024 MfaText Contributors <mfatext@example.com> - 1.0.0-1
- Initial release

