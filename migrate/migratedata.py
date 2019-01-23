#!/usr/bin/env python3
#
# Migrador de dados MSSQL Server
#

import math
import sys
from os import listdir, path
from sqlalchemy import create_engine, select, MetaData, Table
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc as sqlalchemyException
from sqlalchemy.engine.reflection import Inspector

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

        if configurations != False:
            self.configurations = configurations

    
    def error(self):
        self.s_source.rollback()
        self.s_target.rollback()
    
        
    def migrate(self, import_folder):
        databases = [f for f in listdir(import_folder) if f.lower().endswith(('.tbl'))]
        
        for database in databases:
            dbname, schema, extension = database.split('.')
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
                    for line in lines:
                        table, condition = line.rstrip().split('|')
                        params = {
                            'dbname': dbname,
                            'schema': schema,
                            'table': table,
                            'condition': condition,
                        }
                        
                        self.copy_data(params)
                except IOError:
                    self.error()
                    
                    print("Arquivo nao encontrado")
                    
        self.s_source.commit()
        self.s_target.commit()
        
        self.s_source.close()
        self.s_target.close()

        self.connection.close()
        
        return True

    def copy_data(self, params):
        
        metadata_source = MetaData(self.engine_source)
        self.s_source = self.Session_source()
        self.s_target = self.Session_target()

        try:        
            table_source = Table(params['table'], metadata_source, autoload=True, autoload_with=self.engine_source, schema=params['schema'])
        except sqlalchemyException.NoSuchTableError:
            self.error()
        
        if params['condition'] == None or params['condition'] == '':
            data_source = self.s_source.query(table_source).all()
        else:
            table_cols = tuple(params['table'] + '.' + col.name for col in table_source.columns)
            if params['condition'].find('JOIN') > 0:
                inspect_table = Inspector.from_engine(self.engine_source)
                pk_field = inspect_table.get_pk_constraint(params['table'], params['schema'])['constrained_columns'][0]
                sql_subquery = "SELECT DISTINCT " + params['table'] + "." + pk_field + " FROM " + params['dbname'] + "." + params['schema'] + "." + params['table'] + " AS " + params['table'] + " " + params['condition'] + " GROUP BY " + params['table'] + "." + pk_field
                sql = "SELECT " + ",".join(table_cols) + " FROM " + params['dbname'] + "." + params['schema'] + "." + params['table'] + " AS " + params['table'] + " WHERE " + params['table'] + "." +  pk_field + " IN (" + sql_subquery + ")"
            else:
                sql = "SELECT " + ",".join(table_cols) + " FROM " + params['dbname'] + "." + params['schema'] + "." + params['table'] + " AS " + params['table'] + " "  + params['condition']

            try:
                result_source = self.s_source.execute(sql).fetchall()
            except sqlalchemyException.IntegrityError as error:
                if (self.configurations['bypass_constrains'] == True):
                    print('Erro de constraint.')
                    pass
                else:
                    print('Erro de constraint:')
                    print(error.message)
                    self.s_target.rollback()
                    exit()                    
                
            resultset = []
            for row in result_source:
                resultset.append(dict(row))

            data_source=resultset
        
        metadata_target = MetaData(self.engine_target)
        table_target = Table(params['table'], metadata_target, autoload=True, autoload_with=self.engine_target, schema=params['schema'])
        
        insert_data = table_target.insert().from_select=data_source
        
        print(' %s.%s.%s' % (params['dbname'], params['schema'], params['table']), end = "")
        
        try:
            for i in range(len(insert_data))[::self.configurations['insert_chain_size']]:
                y = i + insert_chain_size
                chunk_data = insert_data[i:y]
                self.connection.execute(table_target.insert(chunk_data))
                
                print(".", end = "")
                sys.stdout.flush()
                
            print("OK (%s itens)" % len(insert_data))
            
        except NameError:
            print(NameError)
            self.s_target.rollback()
            return False
