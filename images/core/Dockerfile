FROM fresh/debian

ENV DEBIAN_FRONTEND=noninteractive

ARG DISTR_VERSION
ARG LICENSE_TOOLS_VERSION
ARG AXIOM_JRE_VERSION=17.0.1715

COPY ./images/core/entrypoint.sh /entrypoint.sh
COPY ./images/core/server.sh /server.sh

RUN --mount=type=bind,source=./distr,target=/tmp/distr_full \
    set -e && \
    mkdir /tmp/core && \
    cd /tmp/core && \
# Dependencies
    apt-get -y update && \
    apt-get -y install apache2 xvfb x11vnc sudo nano python3 libodbc1 odbc-postgresql net-tools icewm xfce4 gdb libxt6 libglib2.0-0 libgtk-3-0 libsoup-gnome2.4-1 libenchant-2-2 libgstreamer-gl1.0-0 libharfbuzz-icu0 iproute2 libwebkit2gtk-4.0-37 chromium python3-selenium dbus wmctrl gawk && \
# OneScript
    wget --no-verbose -O /tmp/core/onescript-engine.deb https://oscript.io/downloads/1_7_0/x64/onescript-engine_1.7.0_all.deb && \
    apt-get -y install /tmp/core/onescript-engine.deb && \
# Axiom JRE
    apt-get -y install /tmp/distr_full/axiomjdk_jre_pro${AXIOM_JRE_VERSION}_linux_amd64_full.deb && \
# Platform
    unzip /tmp/distr_full/server64_*.zip -d /tmp/core/platform && \
    /tmp/core/platform/setup-full-$DISTR_VERSION-x86_64.run --mode unattended --enable-components client_full,server,liberica_jre,ws,ru,uk,pl,vi,it,ro && \
# License Tools
    mkdir /tmp/core/license_tools && \
    tar -xf /tmp/distr_full/1c_enterprise_license_tools_${LICENSE_TOOLS_VERSION}_linux_x86_64.tar.gz -C /tmp/core/license_tools && \
    /tmp/core/license_tools/1ce-installer-cli install --ignore-signature-warnings && \
# Misc
    update-ca-certificates && \
    opm install deployka && \
    a2enmod headers && \
    localedef -i ru_RU -f UTF-8 ru_RU && \
# Cleanup
    rm -rf /tmp/core && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get -y remove xscreensaver && \
    apt-get -y autoremove && \
    apt-get -y clean && \
# Symlinks
    ln -s /opt/1cv8/x86_64/$DISTR_VERSION /opt/1c && \
    if [ ! -f /usr/lib/x86_64-linux-gnu/libenchant.so.1 ]; then ln -s /usr/lib/x86_64-linux-gnu/libenchant-2.so.2 /usr/lib/x86_64-linux-gnu/libenchant.so.1;fi && \
    touch /etc/sudoers.d/www-data && \
    echo "www-data ALL =NOPASSWD: /usr/sbin/apachectl graceful" >> /etc/sudoers.d/www-data && \
    echo "www-data ALL =NOPASSWD: /usr/sbin/apachectl graceful-stop" >> /etc/sudoers.d/www-data && \
    echo "www-data ALL =NOPASSWD: /usr/sbin/apachectl start" >> /etc/sudoers.d/www-data && \
    echo "www-data ALL =NOPASSWD: /opt/1c/webinst" >> /etc/sudoers.d/www-data && \
    echo "Defaults:www-data !requiretty" >> /etc/sudoers.d/www-data && \
    chmod 0440 /etc/sudoers.d/www-data && \
    touch /etc/sudoers.d/usr1cv8 && \
    echo "usr1cv8 ALL =NOPASSWD: /usr/sbin/apachectl graceful" >> /etc/sudoers.d/usr1cv8 && \
    echo "usr1cv8 ALL =NOPASSWD: /usr/sbin/apachectl graceful-stop" >> /etc/sudoers.d/usr1cv8 && \
    echo "usr1cv8 ALL =NOPASSWD: /usr/sbin/apachectl start" >> /etc/sudoers.d/usr1cv8 && \
    echo "usr1cv8 ALL =NOPASSWD: /opt/1c/webinst" >> /etc/sudoers.d/usr1cv8 && \
    echo "Defaults:usr1cv8 !requiretty" >> /etc/sudoers.d/usr1cv8 && \
    cp /usr/bin/chromium /usr/bin/chromium-real && \
    chmod 0440 /etc/sudoers.d/usr1cv8 && \
    chmod +x /entrypoint.sh


ENV LANG=ru_RU.UTF-8
ENV PATH=$PATH:/opt/1c
ENV COREDATA=/var/lib/1c/data
ENV LIC_DATA=/var/1C/licenses
ENV VOLUMES_PATH=/volumes
ENV MNT_PATH=/mnt
ENV DUMP_PATH=/var/dumps
ENV CORELOGS=/var/log/1c
ENV EXECUTOR_HOME=/opt/executor
ENV EXECUTOR_DATA=/executor-server
ENV FRESH=/var/www/fresh

ENTRYPOINT [ "/entrypoint.sh" ]
