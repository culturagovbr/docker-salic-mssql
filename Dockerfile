
FROM mcr.microsoft.com/mssql/server:latest
MAINTAINER Cleber Santos <oclebersantos@gmail.com>

VOLUME /docker-entrypoint-initdb.d
EXPOSE 1433

# RUN ln -s /opt/mssql-tools/bin/bcp /usr/local/bin/bcp

COPY docker-entrypoint.sh /usr/local/bin/
COPY docker-entrypoint-initdb.sh /usr/local/bin/

COPY . /tmp/
COPY docker-entrypoint-initdb.d /tmp/docker-entrypoint-initdb.d

RUN chmod +x /usr/local/bin/docker-entrypoint.sh && chmod +x /usr/local/bin/docker-entrypoint-initdb.sh && chmod +x /tmp/migrate/main.py

WORKDIR "/tmp/"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]