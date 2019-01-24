#!/bin/bash

# wait for database to start...
for i in {30..0}; do
  if sqlcmd -U SA -P $MSSQL_SA_PASSWORD -Q 'SELECT 1;' &> /dev/null; then
    echo "$0: SQL Server started"
    break
  fi
  echo "$0: SQL Server startup in progress..."
  sleep 1
done

echo "$0: Initializing database"
for f in /docker-entrypoint-initdb.d/*; do
  case "$f" in
    *.sh)     echo "$0: running $f"; . "$f" ;;
    *.sql)    echo "$0: running $f"; sqlcmd -U SA -P $MSSQL_SA_PASSWORD -X -i  "$f"; echo ;;
    *)        echo "$0: ignoring $f" ;;
  esac
  echo
done
echo "$0: SQL Server Database ready"

for entry in $(ls schemas/*.bak)
do
  echo importando $entry
  shortname=$(echo $entry | cut -f 1 -d '.' | cut -f 2 -d '/')
  echo executing $shortname
  /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "salic@123456" -Q 'RESTORE FILELISTONLY FROM DISK = "/tmp/schemas/'$shortname'.bak"' | tr -s ' ' | cut -d ' ' -f 1-2
  /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "salic@123456" -Q 'RESTORE DATABASE '$shortname' FROM DISK = "/tmp/schemas/'$shortname'.bak" WITH MOVE "'$shortname'_Est" TO "/var/opt/mssql/data/'$shortname'_Est.mdf", MOVE "'$shortname'_Est_log" TO "/var/opt/mssql/data/'$shortname'_Est_log.ldf"'
done

echo "$0: Loads initial data..."
cd /tmp/migrate
./main.py migrate 0-initial
