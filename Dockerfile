
FROM mcr.microsoft.com/mssql/server:latest
MAINTAINER Cleber Santos <oclebersantos@gmail.com>

VOLUME /docker-entrypoint-initdb.d
EXPOSE 1433

# RUN ln -s /opt/mssql-tools/bin/bcp /usr/local/bin/bcp

COPY docker-entrypoint.sh /usr/local/bin/
COPY docker-entrypoint-initdb.sh /usr/local/bin/

RUN apt update && apt install -y \
python3-pip \
unixodbc-dev

RUN pip3 install --upgrade pip
RUN pip install pyodbc sqlalchemy

RUN chmod +x /usr/local/bin/docker-entrypoint.sh 
RUN chmod +x /usr/local/bin/docker-entrypoint-initdb.sh

COPY schemas /tmp/schemas
COPY initial-data.sql /tmp/initial-data.sql
COPY migrate /tmp/migrate
RUN chmod +x /tmp/migrate/main.py

WORKDIR "/tmp/"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]