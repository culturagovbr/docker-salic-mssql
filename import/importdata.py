#!/usr/bin/python
#
# Importador de dados MSSQL Server


from os import listdir, path
from sqlalchemy import create_engine, select, MetaData, Table, sessionmaker
class importdata:

    db_source = {}
    db_target = {}
    dsn_source = ''
    dsn_target = ''

    def __init__(self, db_source, db_target):
        self.db_source = db_source
        self.db_target = db_target
        
        self.set_dsn()
            
    def set_dsn(self):
        alchemy_driver = 'mssql+pyodbc'
        odbc_driver = 'ODBC+Driver+17+for+SQL+Server'
        
        self.dsn_source = ('%s://%s:%s@%s:%s/%s?driver=%s') % (
            alchemy_driver,
            self.db_source.get('user'),
            self.db_source.get('pass'),
            self.db_source.get('host'),
            self.db_source.get('port'),
            self.db_source.get('database'),
            odbc_driver,
        )
        self.dsn_target = ('%s://%s:%s@%s:%s/%s?driver=%s') % (
            alchemy_driver,
            self.db_target.get('user'),
            self.db_target.get('pass'),
            self.db_target.get('host'),
            self.db_target.get('port'),
            self.db_target.get('database'),
            odbc_driver,
        )
    
    
    def prepare_queries(self, import_folder):
        databases = [f for f in listdir(import_folder) if f.lower().endswith(('.tbl'))]
        
        for database in databases:
            filename = path.join(import_folder, database)
            with open(filename) as f:
                try:
                    lines = f.readlines()
                    for line in lines:
                        table, condition = line.rstrip().split('|')
                        dbname, schema, extension = database.split('.')
                        
                        params = {
                            'dbname': dbname,
                            'schema': schema,
                            'table': table,
                            'condition': condition,
                        }
                        
                        self.copy_data(params)
                except IOError:
                    print "Arquivo não encontrado"
                
        return True
    
    def copy_data(self, params):

        try:
            engine_source = create_engine(self.dsn_source)
            engine_target = create_engine(self.dsn_target)
            
            metadata_source = MetaData(engine_source)
            table_source = Table(params.get('table'), metadata_source, autoload=True, autoload_with=en, schema=params.get('schema'))

            conn_source = engine_source.connect()
            select_source = select([table_source]).where(params.get('condition'))
            result_source = conn_source.execute(select_source)

            conn_target = engine_target.connect()
            
            metadata_target = MetaData(engine_target)
            table_target = Table(params.get('table'), metadata_target, autoload=True, autoload_with=en, schema=params.get('schema'))
            
            # proximos passos:
            # a partir do result_source, adicionar no target
            
        except subprocess.CalledProcessError as e:
            print "Erro ao executar query: %" % (e.output)
        
        return True
