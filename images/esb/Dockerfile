FROM fresh/debian

ENV DEBIAN_FRONTEND=noninteractive

ARG DISTR_VERSION

ENV LANG=ru_RU.UTF-8

RUN --mount=type=bind,source=./distr,target=/tmp/distr_full \
    apt-get -y update && \
    mkdir /tmp/esb && \
    tar -xf /tmp/distr_full/1c_enterprise_esb*.tar.gz -C /tmp/esb && \
    export LONG_VER="$(/tmp/esb/1ce-installer-cli query 1c-enterprise-esb | grep version | sed 's/version: //')" && \
    echo $LONG_VER && \
    /tmp/esb/1ce-installer-cli install --disable-service-creation --ignore-hardware-checks && \
    ln -s  "/opt/1C/1CE/components/1c-enterprise-esb-$LONG_VER-x86_64/bin/esb" "/opt/1C/1CE/components/esbstart" && \
    rm -rf /tmp/esb && \
    apt-get -y autoremove && \
    apt-get -y clean

COPY ./images/esb/integrationBus.yml /var/opt/1C/1CE/instances/1c-enterprise-esb/config
COPY ./images/esb/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "/opt/1C/1CE/components/esbstart start --instance /var/opt/1C/1CE/instances/1c-enterprise-esb"]
