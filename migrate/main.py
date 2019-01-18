#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from migratedata import MigrateData
import sys
import os

############################
## Configure a partir daqui

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

## Configure até aqui
##########################

tables_folder = 'tables'
workdir = os.path.join(os.getcwd(), tables_folder)
available_migrations = os.listdir(workdir)

def display_available(available):
    for m in available:
        print(' * %s' % m)
    

if len(sys.argv) > 1:
    folder = sys.argv[1]

    if available_migrations.__contains__(folder) == True:
        migrate_data = MigrateData(db_source, db_target)
        migrate_folder = os.path.join(tables_folder, folder)
        migrate_data.migrate(migrate_folder)
        
    else:
        print('Migração informada não existe! Escolha uma das abaixo:')
        display_available(available_migrations)
        exit()

else:
    print("Escolha dentre os conjuntos de tabelas abaixo qual você deseja importar:")
    display_available(available_migrations)    
    exit()
