#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from migratedata import MigrateData
from dbconfig import db_config
import sys
import os

configurations = {
    'bypass_constrains': True,
    'insert_chain_size': 10,
    'tables_folder': 'tables',
    'exclude_column_types': ('timestamp'),
    'file_mapping_name': 'mapping-db.txt'
}

#############################
### definicoes de metodos ###
#############################

def get_available_migrations():
    workdir = os.path.join(os.getcwd(), configurations['tables_folder'])
    return os.listdir(workdir)

def display_available():
    print("\033[92m")
    for m in get_available_migrations():
        print(' * %s' % m)
    print('\033[0m')

def help_menu():
    print(" ")
    print("Uso: ./main.py [acao]")
    print(" migrate [conjunto de tabelas]           Realiza tarefas de migracao descritas na pasta do conjunto de tabelas (pasta migrate/tables)")
    print(" flush [conjunto de tabelas]             Limpa registros do conjunto de tabelas especificado")
    print(" map                                     Mapeia o banco de dados e relacionamentos")
    print(" grab [tabela|condicoes] [opcoes]        Busca todos os dados relacionados a 'tabela|id=123', entre aspas")
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
    if get_available_migrations().__contains__(folder) == True:
        migrate_data = MigrateData(db_config, configurations)
        migrate_folder = os.path.join(configurations['tables_folder'], folder)
        migrate_data.migrate(migrate_folder)
        
    else:
        print('Escolha um conjunto valido de tabelas para migrar! Escolha uma das abaixo:')
        display_available()
        exit()
        
def flush(folder):
    if get_available_migrations().__contains__(folder) == True:
        migrate_data = MigrateData(db_config, configurations)
        migrate_folder = os.path.join(configurations['tables_folder'], folder)
        migrate_data.flush(migrate_folder)
    else:
        print('Escolha um conjunto valido de tabelas para limpar! Escolha uma das abaixo:')
        display_available()
        exit()

def map_database():
    migrate_data = MigrateData(db_config, configurations)
    migrate_data.map_database()

def grab_data():
    if (len(sys.argv) < 3):
        print("Exemplo de uso:")
        print("$ ./main.py grab 'db.schema.tabela|idTabela=123' --map --get-related")
        exit()
    
    options_available = ('--map', '--get-related')
    
    command, action, query, *options, = sys.argv
    
    if '--' in query or '|' not in query:
        print("Query invalida!")
        print("Exemplo de uso:")
        print("$ ./main.py grab 'db.schema.tabela|idTabela=123' --map --get-related")
        exit()
    
    if set(options) <= set(options_available):
        migrate_data = MigrateData(db_config, configurations)
        migrate_data.grab_data(query, options)
        
    else:
        for option in options:
            if option not in options_available:
                print("Comando %s nao encontrado." % (option))
                exit()    
    
def main():    
    if len(sys.argv) > 1:
        actions = ('help', 'migrate', 'flush', 'map', 'grab')
        commands = ('command', 'action', 'folder')

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
            elif action == 'map':
                map_database()
            elif action == 'grab':
                grab_data()
            else:
                help_menu()           
        else:
            print("Acao %s nao encontrada." % (action))
            help_menu()
    else:
        help_menu()


#############################
###     inicializacao     ###
#############################

main()
