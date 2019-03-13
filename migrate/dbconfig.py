#!/usr/bin/env python3
# -*- coding: utf-8 -*-

db_config = {
    "db_source": {
        "host": "10.0.0.205",
        "user": "usuarios_internet",
        "pass": "salic",
        "port": "1434",
        "dbname": "sac",
        "schema": "dbo",
    },
    "db_target": {
        "host": "localhost",
        "user": "SA",
        "pass": "salic@123456",
        "port": "1433",
        "dbname": "sac",
        "schema": "dbo",
    }
}

db_names = [
    'agentes.dbo',
    'sac.dbo',
    'tabelas.dbo',
    'controledeacesso.dbo',
    'BDCORPORATIVO.scCorp',
    'bdcorporativo.scSAC',
    'bddne.scdne'
]
