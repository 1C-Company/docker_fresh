FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN \
    apt-get -y update ;\
    apt-get -y upgrade ;\
    apt-get -y install tzdata locales ca-certificates wget gosu gnupg gnupg2 procps dbus-x11 cifs-utils jq curl unzip ;\
    localedef -f UTF-8 -i ru_RU ru_RU.UTF-8 ;\
    ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime ;\
    dpkg-reconfigure -f noninteractive tzdata ;\
    apt-get -y autoremove ;\
    apt-get -y clean

ENV LANG=ru_RU.utf8
ENV DISPLAY=:99

ADD ./images/debian/fonts/msttcorefonts.tar.gz /usr/share/fonts/truetype/msttcorefonts/