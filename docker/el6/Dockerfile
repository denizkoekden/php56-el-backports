FROM centos:6.10

# CentOS 6 and EPEL 6 are end of life; packages come from the archives and are checked against the CentOS
# key from the image and the EPEL key stored next to this file (fingerprint 8C3B E96A … 0608 B895).
COPY RPM-GPG-KEY-EPEL-6 /etc/pki/rpm-gpg/
RUN rm -f /etc/yum.repos.d/*.repo \
 && printf '%s\n' \
    '[base]' 'name=CentOS 6.10 base' 'baseurl=https://vault.centos.org/6.10/os/x86_64/' \
    'gpgcheck=1' 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6' \
    '[updates]' 'name=CentOS 6.10 updates' 'baseurl=https://vault.centos.org/6.10/updates/x86_64/' \
    'gpgcheck=1' 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6' \
    '[epel]' 'name=EPEL 6 archive' 'baseurl=https://archives.fedoraproject.org/pub/archive/epel/6/x86_64/' \
    'gpgcheck=1' 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6' \
    > /etc/yum.repos.d/build.repo \
 && rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6 /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6 \
 && rpm -q gpg-pubkey-0608b895 \
 && yum -y -q install \
    rpm-build gcc gcc-c++ make autoconf automake libtool bison flex re2c patch xz tar which file perl \
    httpd-devel libxml2-devel openssl-devel bzip2-devel libcurl-devel libjpeg-turbo-devel libpng-devel \
    freetype-devel libXpm-devel gmp-devel libicu-devel libxslt-devel openldap-devel cyrus-sasl-devel \
    libc-client-devel krb5-devel libmcrypt-devel postgresql-devel sqlite-devel libedit-devel zlib-devel \
 && yum clean all
