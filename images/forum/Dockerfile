FROM tomcat:9-jdk17-temurin

ENV JAVA_OPTS="${JAVA_OPTS} -Xms256m -Xmx512m -XX:+UseParallelGC -server"

RUN rm -rf /usr/local/tomcat/webapps/* && \
    mkdir -p /var/www/forum/{mess_files,logo} 

COPY ./images/forum/distr/forum/ROOT.war /usr/local/tomcat/webapps/

EXPOSE 8080

CMD ["bin/catalina.sh", "run"]