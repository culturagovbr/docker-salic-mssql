#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from migratedata import MigrateData
import sys
import os

############################
## Configure a partir daqui

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

configurations = {
    'bypass_constrains': True,
    'insert_chain_size': 10,
}

## Configure até aqui
##########################

tables_folder = 'tables'
workdir = os.path.join(os.getcwd(), tables_folder)
available_migrations = os.listdir(workdir)

def display_available(available):
    print("\033[92m")
    for m in available:
        print(' * %s' % m)
    

    print('\033[0m')


def help_menu():
    print(" ")
    print("Uso: ./main.py [acao]")
    print(" migrate [conjunto de tabelas]           Realiza tarefas de migracao descritas na pasta do conjunto de tabelas (pasta migrate/tables)")
    print(" flush [conjunto de tabelas]             Limpa registros do conjunto de tabelas especificado")
    print(" help                                    Exibe esta tela de ajuda")    
        
def show_header():
    print("""\033[32m""" + """
           oo                                                       dP oo          
                                                                    88             
88d8b.d8b. dP .d8888b. 88d888b. .d8888b.          .d8888b. .d8888b. 88 dP .d8888b.  """ + """\033[33m""" + """
88'`88'`88 88 88'  `88 88'  `88 88'  `88 88888888 Y8ooooo. 88'  `88 88 88 88'  `"" 
88  88  88 88 88.  .88 88       88.  .88                88 88.  .88 88 88 88.  ...  """ + """\033[31m""" + """
dP  dP  dP dP `8888P88 dP       `88888P8          `88888P' `88888P8 dP dP `88888P' 
                   .88                                                              """ + """\033[31m """ + """
               d8888P                                                               """)
    print('\033[0m')

def migrate(folder = None):
    if available_migrations.__contains__(folder) == True:
        migrate_data = MigrateData(db_config, configurations)
        migrate_folder = os.path.join(tables_folder, folder)
        migrate_data.migrate(migrate_folder)
        
    else:
        print('Escolha um conjunto valido de tabelas para migrar! Escolha uma das abaixo:')
        display_available(available_migrations)
        exit()
        
def flush(folder):
    if available_migrations.__contains__(folder) == True:
        migrate_data = MigrateData(db_config, configurations)
        migrate_folder = os.path.join(tables_folder, folder)
        migrate_data.flush(migrate_folder)
    else:
        print('Escolha um conjunto valido de tabelas para limpar! Escolha uma das abaixo:')
        display_available(available_migrations)
        exit()    

    
actions = ('help', 'migrate', 'flush')


if len(sys.argv) > 1:
    commands = ['command', 'action', 'folder']
    args = dict(zip(commands, sys.argv))
    
    action = args['action']
    
    if 'folder' in args:
        folder = args['folder']
    else:
        folder = None
    
    if action in actions:
        if action == 'help':
            show_header()
            help_menu()
        elif action == 'migrate':
            migrate(folder)
        elif action == 'flush':
            flush(folder)
        else:
            help_menu()
    
    else:
        print("Acao %s nao encontrada." % (action))
        error_menu()
        
else:
    help_menu()
