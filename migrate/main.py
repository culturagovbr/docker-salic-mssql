#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from migratedata import MigrateData

db_source = {
#    "host": "MCSRV205\MSSQLSERVER2012",
    "host": "10.0.0.205",
    "user": "usuarios_internet",
    "pass": "salic",
    "port": "1434",
    "dbname": "sac",
}

db_target = {
    "host": "localhost",
    "user": "SA",
    "pass": "salic@123456",
    "port": "1433",
    "dbname": "sac",
}


migrate_data = MigrateData(db_source, db_target)

migrate_folder = '/tmp/migrate/initial'
migrate_data.migrate(migrate_folder)

