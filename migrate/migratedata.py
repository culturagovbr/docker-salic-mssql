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

    def __init__(self, db_source, db_target):
        self.db_source = db_source
        self.db_target = db_target
        
        self.configure()
    
    def set_dsn(self):
        alchemy_driver = 'mssql+pyodbc'
        odbc_driver = 'ODBC+Driver+17+for+SQL+Server'
        
        self.dsn_source = ('%s://%s:%s@%s:%s/%s?driver=%s') % (
            alchemy_driver,
            self.db_source.get('user'),
            self.db_source.get('pass'),
            self.db_source.get('host'),
            self.db_source.get('port'),
            self.db_source.get('dbname'),
            odbc_driver,
        )
        self.dsn_target = ('%s://%s:%s@%s:%s/%s?driver=%s') % (
            alchemy_driver,
            self.db_target.get('user'),
            self.db_target.get('pass'),
            self.db_target.get('host'),
            self.db_target.get('port'),
            self.db_target.get('dbname'),
            odbc_driver,
        )

    def configure(self):
        self.set_dsn()
        
        self.engine_source = create_engine(self.dsn_source)
        self.engine_target = create_engine(self.dsn_target)

        self.Session_source = sessionmaker(bind=self.engine_source)
        self.Session_target = sessionmaker(bind=self.engine_target)

        self.connection = self.engine_target.connect()

    
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

            if dbname != self.db_source.get('dbname') or schema != self.db_source.get('schema'):
                self.db_source.__setitem__('dbname', dbname)
                self.db_target.__setitem__('dbname', dbname)
                self.db_source.__setitem__('schema', schema)
                self.db_target.__setitem__('schema', schema)
                
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
            table_source = Table(params.get('table'), metadata_source, autoload=True, autoload_with=self.engine_source, schema=params.get('schema'))
        except sqlalchemyException.NoSuchTableError:
            self.error()
        
        if params.get('condition') == None or params.get('condition') == '':
            data_source = self.s_source.query(table_source).all()
        else:
            table_cols = tuple(params.get('table') + '.' + col.name for col in table_source.columns)
            if params.get('condition').find('JOIN') > 0:
                sql = "SELECT DISTINCT " + ",".join(table_cols) + " FROM " + params.get('dbname') + "." + params.get('schema') + "." + params.get('table') + " AS " + params.get('table') + " "  + params.get('condition') + " GROUP BY " + ",".join(table_cols)
            else:
                sql = "SELECT " + ",".join(table_cols) + " FROM " + params.get('dbname') + "." + params.get('schema') + "." + params.get('table') + " AS " + params.get('table') + " "  + params.get('condition')
            
            result_source = self.s_source.execute(sql).fetchall()

            resultset = []
            for row in result_source:
                resultset.append(dict(row))

            data_source=resultset
        
        metadata_target = MetaData(self.engine_target)
        table_target = Table(params.get('table'), metadata_target, autoload=True, autoload_with=self.engine_target, schema=params.get('schema'))
        
        insert_data = table_target.insert().from_select=data_source
        
        # chain size for inserting # 100 per insert
        insert_chain_size = 10
        print(' %s.%s.%s' % (params.get('dbname'), params.get('schema'), params.get('table')), end = "")
        
        try:
            for i in range(len(insert_data))[::insert_chain_size]:
                y = i + insert_chain_size - 1
                chunk_data = insert_data[i:y]
                self.connection.execute(table_target.insert(chunk_data))
                
                print(".", end = "")
                sys.stdout.flush()
                
            print("OK (%s itens)" % len(insert_data))
            
        except NameError:
            print(NameError)
            self.s_target.rollback()
            return False
