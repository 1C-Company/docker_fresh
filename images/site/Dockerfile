FROM bellsoft/liberica-openjdk-debian:17

COPY ./images/site/distr/site/ROOT.war /usr/share/site/site.war

ENV \
    JAVA_OPTS="-Xmx256M" \
    SERVER_PORT=8080 \
    MANAGEMENT_SERVER_PORT=8081 \
    SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/site?ApplicationName=site \
    SPRING_DATASOURCE_USERNAME=postgres \
    SPRING_DATASOURCE_PASSWORD=postgres \
    LOGGING_FILE_PATH=/var/log/site/ \
    SERVER_TOMCAT_ACCESSLOG_ENABLED=TRUE \
    SERVER_TOMCAT_ACCESSLOG_DIRECTORY=/var/log/site/

RUN \
    apt-get -y update ;\
    apt-get -y upgrade ;\
    apt-get -y install wget

CMD java $JAVA_OPTS -jar /usr/share/site/site.war