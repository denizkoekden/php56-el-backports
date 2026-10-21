# PHP 5.6 for CentOS/RHEL 6 and 7, built from upstream 5.6.40 plus the complete patch series of
# Ondřej Surý's Debian packaging (deb.sury.org), which backports security fixes from current PHP.
# Installs into /opt/php56 so it can sit next to the distribution PHP; nothing is enabled automatically.

%global inst      /opt/php56
%global sury_ver  104+0~20261021.134+ubuntu24.04~1.gbp7401dd
%global sury_rev  104
%global apxs      %(test -x /usr/bin/apxs && echo /usr/bin/apxs || echo /usr/sbin/apxs)
%global debug_package %{nil}

# Extension modules are plugins, not shared libraries other packages should link against.
%global __provides_exclude_from ^%{inst}/.*\\.so$
%{?filter_provides_in: %filter_provides_in %{inst}/.*\.so$}
%{?filter_setup}

Name:           php56
Version:        5.6.40
Release:        %{sury_rev}.1%{?dist}
Summary:        PHP 5.6 with backported security fixes, installed in %{inst}
License:        PHP and Zend and BSD and MIT
URL:            https://github.com/denizkoekden/php56-el-backports
Source0:        php5.6_%{version}.orig.tar.xz
Source1:        php5.6_%{version}-%{sury_ver}.debian.tar.xz

BuildRequires:  gcc gcc-c++ make autoconf automake libtool bison flex re2c patch xz
BuildRequires:  httpd-devel libxml2-devel openssl-devel bzip2-devel libcurl-devel libjpeg-turbo-devel
BuildRequires:  libpng-devel freetype-devel libXpm-devel gmp-devel libicu-devel libxslt-devel
BuildRequires:  openldap-devel cyrus-sasl-devel libc-client-devel krb5-devel libmcrypt-devel
BuildRequires:  postgresql-devel libedit-devel zlib-devel sqlite-devel
%if 0%{?rhel} >= 7
BuildRequires:  systemd-devel
%endif

%description
PHP 5.6.40 with the security backports maintained by Ondřej Surý for Debian and Ubuntu, rebuilt for
Enterprise Linux. Ships the CLI, CGI/FastCGI and FPM binaries, the Apache 2 module as
%{_libdir}/httpd/modules/libphp56.so and the common extensions as shared modules. Everything lives in
%{inst}; the distribution PHP is left untouched and nothing is activated automatically.

%package imap
Summary:        IMAP extension for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description imap
The imap extension for %{name}.

%package mcrypt
Summary:        mcrypt extension for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description mcrypt
The mcrypt extension for %{name}.

%package gd
Summary:        GD extension for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description gd
The gd extension for %{name}.

%package pgsql
Summary:        PostgreSQL extensions for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description pgsql
The pgsql and pdo_pgsql extensions for %{name}.

%prep
%setup -q -n php-%{version}
xz -dc %{SOURCE1} | tar -xf -
# Patches left out on purpose (see README): not security fixes, and they add behaviour or dependencies
# that do not belong in these packages.
skip=" 0251-Add-minimal-privacy-preserving-secure-DNS-telemetry-.patch "
while read -r p; do
    case "$p" in ''|'#'*) continue ;; esac
    case "$skip" in *" $p "*) echo "skipping $p"; continue ;; esac
    patch -p1 -F0 -s < "debian/patches/$p" || { echo "patch failed: $p"; exit 1; }
done < debian/patches/series
rm -rf debian
# Same steps as debian/rules: ext_skel becomes a configure output, then the build system is regenerated.
# aclocal.m4 must go first: it carries the same timestamp as the patched files, so make would skip aclocal
# and miss pkg.m4.
[ -f ext/ext_skel ] && mv ext/ext_skel ext/ext_skel.in
rm -f aclocal.m4 configure
./buildconf --force

%build
# ICU 4.2 on EL6 has no pkg-config files, so configure falls back to icu-config, whose --cxxflags carry
# "-ansi -pedantic". The intl extension compiles its C files with those flags too, which fails. A wrapper
# earlier in PATH drops them; with ICU from pkg-config (EL7) it is never called.
mkdir -p icu-wrap
cat > icu-wrap/icu-config <<'EOF'
#!/bin/sh
/usr/bin/icu-config "$@" | sed -e 's/ -ansi//g' -e 's/ -pedantic//g'
EOF
chmod +x icu-wrap/icu-config
export PATH="$PWD/icu-wrap:$PATH"

COMMON="--prefix=%{inst} --exec-prefix=%{inst} --sysconfdir=%{inst}/etc --localstatedir=%{inst}/var \
 --with-config-file-path=%{inst}/etc --with-config-file-scan-dir=%{inst}/etc/php.d \
 --with-libdir=%{_lib} --mandir=%{inst}/share/man \
 --disable-debug --with-pic --disable-rpath --without-pear --disable-phpdbg --with-system-tzdata \
 --with-openssl --with-zlib --with-bz2 --with-gettext --with-gmp --with-iconv --with-mhash --with-kerberos \
 --enable-exif --enable-ftp --enable-sockets --enable-shmop --enable-calendar --enable-pcntl \
 --with-libxml-dir=/usr --enable-xml --with-libedit --enable-mbregex \
 --with-imap=shared --with-imap-ssl --enable-mbstring=shared \
 --with-gd=shared --with-freetype-dir=/usr --with-png-dir=/usr --with-xpm-dir=/usr --with-jpeg-dir=/usr \
 --enable-gd-native-ttf --enable-bcmath=shared --with-xmlrpc=shared --with-ldap=shared --with-ldap-sasl \
 --enable-mysqlnd=shared --with-mysql=shared,mysqlnd --with-mysqli=shared,mysqlnd \
 --with-mysql-sock=/var/lib/mysql/mysql.sock --enable-dom=shared --with-pgsql=shared --enable-wddx=shared \
 --enable-soap=shared --with-xsl=shared,/usr --enable-xmlreader=shared --enable-xmlwriter=shared \
 --with-curl=shared,/usr --enable-pdo=shared --with-pdo-mysql=shared,mysqlnd --with-pdo-pgsql=shared,/usr \
 --with-pdo-sqlite=shared,/usr --with-sqlite3=shared,/usr --enable-json=shared --enable-zip=shared --enable-phar=shared \
 --with-mcrypt=shared,/usr --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
 --enable-posix=shared --enable-fileinfo=shared --enable-intl=shared --enable-opcache=shared"

# Pass 1: Apache 2 module only (same builtin set as pass 2, so the shared extensions fit both).
mkdir build-apache
pushd build-apache
../configure $COMMON --with-apxs2=%{apxs} --disable-cgi --enable-cli
make %{?_smp_mflags} libphp5.la
popd

# Pass 2: CLI, CGI/FastCGI, FPM and all shared extensions.
mkdir build-cgi
pushd build-cgi
../configure $COMMON --enable-cli --enable-cgi --enable-fpm --with-fpm-user=apache --with-fpm-group=apache \
%if 0%{?rhel} >= 7
  --with-fpm-systemd
%endif

make %{?_smp_mflags}
popd

%install
pushd build-cgi
make install INSTALL_ROOT=%{buildroot}
popd
install -D -m 0755 build-apache/libs/libphp5.so %{buildroot}%{_libdir}/httpd/modules/libphp56.so
install -D -m 0644 php.ini-production %{buildroot}%{inst}/etc/php.ini

# One ini file per shared extension; load order keeps mysqlnd, pdo and dom ahead of their dependents.
extdir=$(ls -d %{buildroot}%{inst}/lib/php/extensions/no-debug-non-zts-*)
mkdir -p %{buildroot}%{inst}/etc/php.d
for so in "$extdir"/*.so; do
    n=$(basename "$so" .so)
    case "$n" in
        opcache) printf '; Not enabled by default.\n;zend_extension=opcache.so\n' > %{buildroot}%{inst}/etc/php.d/10-opcache.ini; continue ;;
        mysqlnd|pdo|json|dom) prio=10 ;;
        mysql|mysqli|pdo_*|xmlreader|xsl|wddx) prio=30 ;;
        *) prio=20 ;;
    esac
    echo "extension=$n.so" > %{buildroot}%{inst}/etc/php.d/$prio-$n.ini
done

install -d %{buildroot}%{inst}/share/doc
cat > %{buildroot}%{inst}/share/doc/httpd-php56.conf.example <<'EOF'
# Example for Apache: replace the distribution's mod_php line with this one (both register php5_module).
LoadModule php5_module modules/libphp56.so
<FilesMatch \.php$>
    SetHandler application/x-httpd-php
</FilesMatch>
DirectoryIndex index.php
EOF
rm -rf %{buildroot}/.channels %{buildroot}/.depdb* %{buildroot}/.filemap %{buildroot}/.lock %{buildroot}/.registry

%files
%{inst}
%config(noreplace) %{inst}/etc/php.ini
%config(noreplace) %{inst}/etc/php.d/*.ini
%{_libdir}/httpd/modules/libphp56.so
%exclude %{inst}/lib/php/extensions/*/imap.so
%exclude %{inst}/etc/php.d/20-imap.ini
%exclude %{inst}/lib/php/extensions/*/mcrypt.so
%exclude %{inst}/etc/php.d/20-mcrypt.ini
%exclude %{inst}/lib/php/extensions/*/gd.so
%exclude %{inst}/etc/php.d/20-gd.ini
%exclude %{inst}/lib/php/extensions/*/pgsql.so
%exclude %{inst}/etc/php.d/20-pgsql.ini
%exclude %{inst}/lib/php/extensions/*/pdo_pgsql.so
%exclude %{inst}/etc/php.d/30-pdo_pgsql.ini

%files imap
%{inst}/lib/php/extensions/*/imap.so
%config(noreplace) %{inst}/etc/php.d/20-imap.ini

%files mcrypt
%{inst}/lib/php/extensions/*/mcrypt.so
%config(noreplace) %{inst}/etc/php.d/20-mcrypt.ini

%files gd
%{inst}/lib/php/extensions/*/gd.so
%config(noreplace) %{inst}/etc/php.d/20-gd.ini

%files pgsql
%{inst}/lib/php/extensions/*/pgsql.so
%{inst}/lib/php/extensions/*/pdo_pgsql.so
%config(noreplace) %{inst}/etc/php.d/20-pgsql.ini
%config(noreplace) %{inst}/etc/php.d/30-pdo_pgsql.ini

%changelog
* Wed Oct 21 2026 Deniz Kökden - 5.6.40-104.1
- Rebuild of the deb.sury.org php5.6 5.6.40-104 patch series for Enterprise Linux 6 and 7,
  including the backported fix for CVE-2026-109618 and CVE-2026-109619.
