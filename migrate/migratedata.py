#!/usr/bin/env python3
#
# Migrador de dados MSSQL Server
#

import math
import sys
import os
from os import listdir, path
import re
from sqlalchemy import create_engine, select, MetaData, Table
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc as sqlalchemyException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.reflection import Inspector
from dbconfig import db_names

class MigrateData:

    db_source = {}
    db_target = {}
    dsn_source = ''
    dsn_target = ''
    Session_source = {}
    Session_target = {}
    s_source = {}
    s_target = {}
    conn = {}
    configurations = {}
    actions = ('migrate', 'flush')
    errors = []
    
    def __init__(self, db_config, configurations):
        if not all(k in db_config.keys() for k in ('db_source', 'db_target')):
            print("Defina db_source e db_target no arquivo main.py!")
            exit()
        
        self.db_source = db_config['db_source']
        self.db_target = db_config['db_target']
        self.configure(configurations)
    
    def set_dsn(self):
        alchemy_driver = 'mssql+pyodbc'
        odbc_driver = 'ODBC+Driver+17+for+SQL+Server'
        
        self.dsn_source = ('%s://%s:%s@%s:%s/%s?driver=%s') % (
            alchemy_driver,
            self.db_source['user'],
            self.db_source['pass'],
            self.db_source['host'],
            self.db_source['port'],
            self.db_source['dbname'],
            odbc_driver,
        )
        self.dsn_target = ('%s://%s:%s@%s:%s/%s?driver=%s') % (
            alchemy_driver,
            self.db_target['user'],
            self.db_target['pass'],
            self.db_target['host'],
            self.db_target['port'],
            self.db_target['dbname'],
            odbc_driver,
        )

    def configure(self, configurations = False):
        self.set_dsn()
        
        self.engine_source = create_engine(self.dsn_source)
        self.engine_target = create_engine(self.dsn_target)
        self.Session_source = sessionmaker(bind=self.engine_source)
        self.Session_target = sessionmaker(bind=self.engine_target)
        self.connection = self.engine_target.connect()

        if configurations:
            self.configurations = configurations

    def error_report(self):
        print("")
        print("#####  ERRO(S) #####")
        print(" %s erro(s) foram encontrados durante a execucao!" % (len(self.errors)))
        print("")
        for e in self.errors:
            print("(%s) - %s" % (e[0], e[1].__context__))

        print("#####  ERRO(S) #####")
        print("%s erro(s) foram encontrados durante a execucao!" % (len(self.errors)))

    def rollback(self):
        if any(self.s_source):
            self.s_source.rollback()
        if any(self.s_target):
            self.s_target.rollback()

    def flush(self, import_folder):
        print("Apagando dados...")
        self.execute(import_folder, 'flush', True)
    
    def migrate(self, import_folder):
        print("Importando dados...")
        self.execute(import_folder, 'migrate')

    def error_append(self, tablename, error):
        self.errors.append((tablename, error))
        
    def execute(self, import_folder, action, reverse = False):
        if action not in self.actions:
            print("Erro: tentando executar acao desconhecida!")
            exit()

        databases = [f for f in listdir(import_folder) if f.lower().endswith(('.tbl'))]
        databases.sort()
        if reverse == True:
            databases.reverse()

        print("Origem: %s" % (self.db_source['host']))
        print("Destino: %s" % (self.db_target['host']))
        
        file_pattern = re.compile("^[0-9]{1,2}\-(.*)\.(.*)\.tbl$")
        
        for database in databases:
            matches = file_pattern.match(database)
            if matches == None: 
                print("Arquivo de tabela (%s) fora do padrao [00]-[nometabela].[schema].tbl. O numeral refere-se a ordem de execucao." % (database))
                print("Exemplos:")
                print("00-agentesc.dbo.tbl")
                print("01-sac.dbo.tbl")
                exit()

            dbname, schema = matches.groups()
            print(" ")
            print("------------------------------------ ")
            print("Banco/Schema:  %s.%s " % (dbname, schema))
            print("------------------------------------ ")            

            if dbname != self.db_source['dbname'] or schema != self.db_source['schema']:
                self.db_source['dbname'] = dbname
                self.db_target['dbname'] = dbname
                self.db_source['schema'] = schema
                self.db_target['schema'] = schema
                self.configure()
                
            filename = path.join(import_folder, database)
            with open(filename) as f:
                try:
                    lines = f.readlines()
                    if reverse == True:
                        lines.reverse()
                        
                    for line in lines:
                        if any(line):
                            table, condition, primarykey = line.rstrip().split('|')
                            params = {
                                'dbname': dbname,
                                'schema': schema,
                                'table': table,
                                'condition': condition,
                                'primarykey': primarykey
                            }
                        
                            if action == 'flush':
                                self.flush_data(params)
                            elif action == 'migrate':
                                self.migrate_data(params)
                except IOError:
                    self.rollback()
                    
                    print("Arquivo não encontrado")

        if any(self.errors):
            self.error_report()

        print("Finalizado")
        
        self.close_connections()

        return True

    def close_connections(self):
        if any(self.s_source):
            self.s_source.commit()
            self.s_source.close()
        if any(self.s_source):
            self.s_target.commit()
            self.s_target.close()

        self.connection.close()

        return True

    def map_database(self):
        
        dbinfo = {k:None for k in db_names}

        for line in db_names:
            dbname, schema = line.split('.')
            self.db_target['dbname'] = dbname
            self.db_source['schema'] = schema
            self.configure()
            
            metadata = MetaData(self.engine_source, schema = schema, reflect = True)
            table_names = {name.split('.')[1]: None for name in metadata.tables}
            inspector = Inspector.from_engine(self.engine_source)
            
            print("Mapeando banco %s.%s" % (dbname, schema))
            sys.stdout.flush()
            
            for tablename in table_names:
                table_names[tablename] = inspector.get_foreign_keys(tablename, schema = schema)

            dbinfo["%s.%s" % (dbname, schema)] = table_names
            
        tables_by_level = [{}]
        level = 0
        interrupt = 10
        while dbinfo:
            dbinfo, tables_by_level = self.check_table_level(dbinfo, tables_by_level, level)
            level +=1
            if level > interrupt:
                break
        
            fd = open(configurations['file_mapping_name'], 'w')
        fd.write(str(tables_by_level))
        file.close()
        
        print("Mapeamento finalizado.")
        
        return True

    def get_tables_by_level(self, exec_map = False):
        try:
            fd = open(configurations['file_mapping_name'], 'r')
            tables_by_level = eval(fd.readfile())
        except FileNotFoundError:
            if (exec_map):
                self.map_database()                
            else: 
                print("ATENCAO: Nao foi feito o mapeamento do banco de dados.")
                print("Execute ./main map antes")
                exit()
        
        return tables_by_level

    def fetch_table(self, params):
        # 1) busca dados da tabela
        # 1.1) busca dependências da tabela
        # 1.2) monta pilha de importação da tabela baseada em tables_by_level
        # 1.3) consulta todos os dados com essas condições
        # 1.4) executa
        
        return []

    def fetch_table_relations(self, params):
        return []
                
    def grab_data(self, query, options):
        options = [i.replace('--', '') for i in options]
        exec_map = False
        get_related = False
        data = {}
        
        if ('map' in options):
            exec_map = True
        if ('get_related' in options):
            get_related = True

        # 1.A) busca tabelas por nível e armazena na variavel 'data'
        tables_by_level = self.get_tables_by_level(exec_map)
        table_info, condition = query.split('|')
        dbname, schema, table = table_info.split('.')
        params = {
            'dbname': dbname,
            'schema': schema,
            'table': table,
            'condition': condition,
            'primarykey': primarykey
        }

        data['main_tables'] = self.fetch_table(params)
        
        # 1.B) caso queria, buscar tabelas relacionadas e arbazena em 'data'
        if get_related:
            data['related_tables'] = self.fetch_table_relations()
        
        # 2) para cada tabela, busca dados da tabela, com parâmetros
        #migrate_data(self, params):
        
        print(dbinfo.keys())
            
    
    def check_table_level(self, dbinfo, tables_by_level, level):
        tables_by_level.append({})
        dbs = list(dbinfo.keys())
        for db in dbs:
            tables = list(dbinfo[db].keys())
            for table in tables:
                if not dbinfo[db][table]:
                    sys.stdout.flush()
                    tables_by_level[0][table] = dbinfo[db].pop(table)
                elif (dbinfo[db][table]):
                    check_tables = []
                    for constraint_field in dbinfo[db][table]:
                        check = False
                        for table_level in tables_by_level:
                            if constraint_field['referred_table'] in table_level or constraint_field['referred_table'] == str(table):
                                check = True
                                break
                            elif constraint_field['referred_table'] == str(table):
                                check = True
                        check_tables.append(check)
                    if False not in check_tables:
                        tables_by_level[level][table] = dbinfo[db].pop(table)
        return [dbinfo, tables_by_level]
    
    def flush_data(self, params):
        metadata = MetaData(self.engine_target)
        table = Table(params['table'], metadata, autoload=True, autoload_with=self.engine_source, schema=params['schema'])
        self.s_target = self.Session_target()

        self.engine_target.execute(table.delete())
        print(' %s.%s.%s ... OK' % (params['dbname'], params['schema'], params['table']))
        sys.stdout.flush()        

    def get_accepted_columns(self, inspector, params, with_schema = False):
        if with_schema == True:
            columns = [params['table'] + '.' + column['name'] for column in inspector.get_columns(params['table'], params['schema']) if column['type'].__visit_name__.lower() not in self.configurations['exclude_column_types']]
        else:
            columns = [column['name'] for column in inspector.get_columns(params['table'], params['schema']) if column['type'].__visit_name__.lower() not in self.configurations['exclude_column_types']]
        return columns 
    
    def migrate_data(self, params):
        
        metadata_source = MetaData(self.engine_source)
        self.s_source = self.Session_source()
        self.s_target = self.Session_target()

        try:
            table_source = Table(params['table'], metadata_source, autoload=True, autoload_with=self.engine_source, schema=params['schema'])
        except sqlalchemyException.NoSuchTableError:
            self.rollback()
        inspector = Inspector.from_engine(self.engine_source)
        if params['condition'] == None or params['condition'] == '':
            columns = self.get_accepted_columns(inspector, params)
            data_source = self.s_source.query(table_source).with_entities(*(table_source.columns[column] for column in columns)).all()
        else:
            columns = self.get_accepted_columns(inspector, params, with_schema = True)
            if params['condition'].find('JOIN') > 0:
                if any(params['primarykey']):
                    pk_field = params['primarykey']
                else:
                    pk_fields = inspector.get_pk_constraint(params['table'], params['schema'])['constrained_columns']
                    if len(pk_fields) > 1:
                        print("Atencao: multiplas chaves primarias encontadas: %s" % (pk_fields))
                    pk_field = pk_fields[0]
                sql_subquery = "SELECT DISTINCT " + params['table'] + "." + pk_field + " FROM " + params['dbname'] + "." + params['schema'] + "." + params['table'] + " AS " + params['table'] + " " + params['condition'] + " GROUP BY " + params['table'] + "." + pk_field
                sql = "SELECT " + ",".join(columns) + " FROM " + params['dbname'] + "." + params['schema'] + "." + params['table'] + " AS " + params['table'] + " WHERE " + params['table'] + "." +  pk_field + " IN (" + sql_subquery + ")"
            else:
                sql = "SELECT " + ",".join(columns) + " FROM " + params['dbname'] + "." + params['schema'] + "." + params['table'] + " AS " + params['table'] + " "  + params['condition']

            try:
                result_source = self.s_source.execute(sql).fetchall()
            except:
                print(sys.exc_info())
                self.error_append(params['table'], e)
                exit()
            
            resultset = []
            for row in result_source:
                resultset.append(dict(row))

            data_source = resultset
        
        metadata_target = MetaData(self.engine_target)
        table_target = Table(params['table'], metadata_target, autoload=True, autoload_with=self.engine_target, schema=params['schema'])
        
        insert_data = table_target.insert().from_select=data_source
        
        print(' %s.%s.%s ' % (params['dbname'], params['schema'], params['table']), end = "")
        
        for i in range(len(insert_data))[::self.configurations['insert_chain_size']]:
            y = i + self.configurations['insert_chain_size']
            chunk_data = insert_data[i:y]

            try:
                self.connection.execute(table_target.insert(chunk_data))
                print(".", end = "")
                sys.stdout.flush()
            
            except IntegrityError as e:
                if (self.configurations['bypass_constrains'] == True):
                    print('\033[31m' + '(x)' + '\033[0m', end = "")
                    self.error_append(params['table'], e)
                    sys.stdout.flush()
                    pass
                else:
                    print('Erro de constraint:')
                    print(e)
                    self.rollback()
                    break
            
        print("OK (%s itens)" % len(insert_data))
