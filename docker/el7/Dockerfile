FROM centos:7.9.2009

# CentOS 7 and EPEL 7 are end of life; packages come from the archives and are checked against the CentOS
# key from the image and the EPEL key stored next to this file (fingerprint 91E9 7D7C … 352C 64E5).
COPY RPM-GPG-KEY-EPEL-7 /etc/pki/rpm-gpg/
RUN rm -f /etc/yum.repos.d/*.repo \
 && printf '%s\n' \
    '[base]' 'name=CentOS 7.9 base' 'baseurl=https://vault.centos.org/7.9.2009/os/x86_64/' \
    'gpgcheck=1' 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' \
    '[updates]' 'name=CentOS 7.9 updates' 'baseurl=https://vault.centos.org/7.9.2009/updates/x86_64/' \
    'gpgcheck=1' 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' \
    '[epel]' 'name=EPEL 7 archive' 'baseurl=https://archives.fedoraproject.org/pub/archive/epel/7/x86_64/' \
    'gpgcheck=1' 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7' \
    > /etc/yum.repos.d/build.repo \
 && rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7 /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 \
 && rpm -q gpg-pubkey-352c64e5 \
 && yum -y -q install \
    rpm-build gcc gcc-c++ make autoconf automake libtool bison flex re2c patch xz tar which file perl \
    httpd-devel libxml2-devel openssl-devel bzip2-devel libcurl-devel libjpeg-turbo-devel libpng-devel \
    freetype-devel libXpm-devel gmp-devel libicu-devel libxslt-devel openldap-devel cyrus-sasl-devel \
    libc-client-devel krb5-devel libmcrypt-devel postgresql-devel sqlite-devel libedit-devel zlib-devel \
    systemd-devel \
 && yum clean all
