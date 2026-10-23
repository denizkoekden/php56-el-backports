# php56-el-backports

PHP 5.6.40 for CentOS/RHEL 6 and 7, rebuilt with the complete patch series that
[Ondřej Surý](https://deb.sury.org/) maintains for Debian and Ubuntu. That series backports security fixes
from current PHP branches to 5.6, including the fix for CVE-2026-109618 and CVE-2026-109619
("Avoid state corruption via bailout", backported from 8.2.35) and, since 5.6.40-105, CVE-2023-0662
(multipart request body DoS, adds the `max_multipart_body_parts` INI setting).

Upstream PHP 5.6 has been end of life since 2019. These packages exist for legacy Enterprise Linux hosts
that cannot move to a current PHP yet. Plan your migration anyway.

## Packages

Everything installs into `/opt/php56`, next to the distribution PHP. Nothing is enabled automatically.

| Package | Contents |
| --- | --- |
| `php56` | CLI (`bin/php`), CGI/FastCGI (`bin/php-cgi`), FPM (`sbin/php-fpm`), Apache module `/usr/lib64/httpd/modules/libphp56.so`, common shared extensions |
| `php56-gd` | gd |
| `php56-imap` | imap |
| `php56-mcrypt` | mcrypt |
| `php56-pgsql` | pgsql, pdo_pgsql |

Configuration lives in `/opt/php56/etc/php.ini` and `/opt/php56/etc/php.d/` (one file per extension).
OPcache is built but disabled by default (`10-opcache.ini`). MySQL support uses mysqlnd.

## Usage

* **CLI:** `/opt/php56/bin/php`
* **FastCGI (mod_fcgid and similar):** point the wrapper to `/opt/php56/bin/php-cgi`.
* **Apache mod_php:** replace the distribution's `LoadModule php5_module …libphp5.so` line with
  `LoadModule php5_module modules/libphp56.so`. Both register `php5_module`, so only one can be loaded.
  See `/opt/php56/share/doc/httpd-php56.conf.example`. The EL6 build works with the stock httpd 2.2 and with
  self-built 2.2.x servers.
* **FPM:** `/opt/php56/sbin/php-fpm`, sample configuration in `/opt/php56/etc/php-fpm.conf.default`.

Switching back means pointing the wrapper or `LoadModule` line at the old PHP again.

## Building

Requires Docker. The script downloads the sources from packages.sury.org, checks their SHA-256 against
`sources.env`, then builds and smoke-tests the RPMs in CentOS 6.10 and 7.9 containers. Base packages come from
the CentOS vault and the EPEL archive, verified with the CentOS keys and the EPEL keys in `docker/`.

```sh
./build.sh          # both
./build.sh el6      # only one
```

The RPMs and SRPM end up in `dist/el6/` and `dist/el7/`.

## Notes

* The sources are the `5.6.40-105` patch set from packages.sury.org, which publishes it as a snapshot build.
  The series is applied unchanged except for the patches listed below; the build system is regenerated, as in
  the Debian build.
* Left out on purpose: `0251-Add-minimal-privacy-preserving-secure-DNS-telemetry-.patch`. It is not a
  security fix, adds network activity to the Apache module and FPM, and pulls in libsodium. These packages are
  meant to carry security fixes only.
* Not affiliated with or supported by deb.sury.org or the PHP project. All credit for the backports goes to
  Ondřej Surý and the Debian PHP maintainers.
* PHP is distributed under the PHP License 3.01; see the `LICENSE` file in the source tarball.
