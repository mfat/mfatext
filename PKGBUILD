# Maintainer: MfaText Contributors <mfatext@example.com>
pkgname=mfatext
pkgver=1.0.0
pkgrel=1
pkgdesc="A feature-rich text editor for GNOME"
arch=('any')
url="https://github.com/mfatext/mfatext"
license=('GPL3')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'gtksourceview5')
makedepends=('python-setuptools')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  python setup.py build
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python setup.py install --root="$pkgdir" --optimize=1 --skip-build
  install -Dm644 data/com.github.mfatext.MfaText.desktop \
    "$pkgdir/usr/share/applications/com.github.mfatext.MfaText.desktop"
  install -Dm644 data/com.github.mfatext.MfaText.metainfo.xml \
    "$pkgdir/usr/share/metainfo/com.github.mfatext.MfaText.metainfo.xml"
}

