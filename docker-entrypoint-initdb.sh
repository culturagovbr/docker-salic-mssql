#!/bin/bash

# wait for database to start...
echo "$0: inicializando dump da estrutura"

for i in {30..0}; do
  if sqlcmd -U SA -P $SA_PASSWORD -Q 'SELECT 1;' &> /dev/null; then
    echo "$0: SQL Server started"
    break
  fi
  echo "$0: SQL Server startup in progress..."
  sleep 1
done

## subir apenas a estrutura
# echo "$0: inicializando dump da estrutura"
# for entry in $(ls schemas/*.bak)
# do
#   echo importando $entry
#   shortname=$(echo $entry | cut -f 1 -d '.' | cut -f 2 -d '/')
#   echo executing $shortname
#   /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P $SA_PASSWORD -Q 'RESTORE FILELISTONLY FROM DISK = "/tmp/schemas/'$shortname'.bak"' | tr -s ' ' | cut -d ' ' -f 1-2
#   /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P $SA_PASSWORD -Q 'RESTORE DATABASE '$shortname' FROM DISK = "/tmp/schemas/'$shortname'.bak" WITH MOVE "'$shortname'" TO "/var/opt/mssql/data/'$shortname'.mdf", MOVE "'$shortname'_log" TO "/var/opt/mssql/data/'$shortname'_log.ldf"'
# done

## subir apenas os dados
# echo "$0: inicializando dump da base"
# for f in docker-entrypoint-initdb.d/*; do
#   echo "carregando $f";
#   case "$f" in
#     *.sh)     echo "$0: running $f"; . "$f" ;;
#     *.sql)    echo "$0: running $f"; /opt/mssql-tools/bin/sqlcmd -U SA -P $SA_PASSWORD -X -i  "$f"; echo ;;
#     *)        echo "$0: ignoring $f" ;;
#   esac
#   echo
# done
# echo "$0: SQL Server Database ready"

## subir estrutura e dados
echo "$0: inicializando dump da estrutura e dados"
for entry in $(ls backup/*.bak)
do
  echo importando $entry
  shortname=$(echo $entry | cut -f 1 -d '.' | cut -f 2 -d '/')
  echo executing $shortname
  /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P $SA_PASSWORD -Q 'RESTORE FILELISTONLY FROM DISK = "/tmp/backup/'$shortname'.bak"' | tr -s ' ' | cut -d ' ' -f 1-2
  /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P $SA_PASSWORD -Q 'RESTORE DATABASE '$shortname' FROM DISK = "/tmp/backup/'$shortname'.bak" WITH MOVE "'$shortname'" TO "/var/opt/mssql/data/'$shortname'.mdf", MOVE "'$shortname'_log" TO "/var/opt/mssql/data/'$shortname'_log.ldf"'
done

# echo "$0: Loads initial data..."
# cd /tmp/migrate
# ./main.py migrate 0-initial
  