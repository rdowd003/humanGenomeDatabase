
import os
import pymysql
import sqlalchemy
import pandas as pd

import humangenomedatabase.hgd_utils as hgd
from configs import auto_config as cfg

class mysqlDataPipe:
    def __init__(self,overwrite=False):
        self.connect()
    
    def connect(self):
        #self.conn = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASS, local_infile=True)
        conn_string = f"mysql+mysqlconnector://[{cfg.DB_USER}]:[{cfg.DB_PASS}]@[{cfg.DB_HOST}]:[3306]/[{cfg.RDS_DB}]"
        self.conn = sqlalchemy.create_engine(conn_string, echo=False)
    

    def write_data(self,db_table,db_table_df,overwrite,chunksize=None):
        if overwrite:
            if_exists = 'overwrite'
        else:
            if_exists = 'append'

        try:
            db_table_df.to_sql(name=db_table,con=self.conn,
                            if_exists=if_exists,
                            index=False,
                            chunksize=chunksize,
                            method="multi")
        except Exception as e:
            print(e)
        
    
    def execute_query_file(self,q_filepath):

        try:
            with open(q_filepath) as file:
                query = sqlalchemy.text(file.read())
                self.conn.execute(query)

        except Exception as e:
            print(e)
            
        finally:
            self.close()
            

    def close(self):
        if self.connection != None:
            self.connection.close()
