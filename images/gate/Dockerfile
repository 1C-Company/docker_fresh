FROM eclipse-temurin:26-jre-noble

RUN --mount=type=bind,source=./distr,target=/tmp/distr_full \
# Dependencies
    apt-get update -y && \
    apt-get install -y --no-install-recommends unzip && \
# Gate install
    unzip /tmp/distr_full/appgate_*.zip -d /tmp/gate && \
    apt-get install -y /tmp/gate/*.deb && \
# Cleanup
    rm -rf /tmp/gate && \
    apt-get remove -y unzip && \
    apt-get autoremove -y && \
# Gate settings
    sed -i -e 's/^# manage\.login=appgate/manage.login=appgate/' -e 's/^# manage\.password=appgate/manage.password=12345Qwer/' /var/lib/appgate/application.properties && \
    echo export PATH=$PATH:/usr/local/openjdk-8/bin > /etc/profile.d/add_java.sh && \
    chmod +x /etc/profile.d/add_java.sh && \
    echo export PATH=$PATH:JAVA_HOME=/usr/local/openjdk-8 > /etc/profile.d/add_java_home.sh && \
    chmod +x /etc/profile.d/add_java_home.sh

EXPOSE 8080 9090

CMD java $JAVA_OPTS -jar /usr/share/appgate/appgate.jar