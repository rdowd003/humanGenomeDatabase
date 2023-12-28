
import os
import pymysql

from configs import auto_config as cfg

class mysqlDataPipe:
    def __init__(self):
        pass
    
    def connect(self):
        self.conn = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASS, local_infile=True)

    def create_table(self,name):
        cursor = self.connection.cursor()

        cursor.execute(f"""drop table if exists {name} """)
        cursor.execute(f"""create table {name}(try VARCHAR(4))""")

        cursor.close()

    def load_data(self,db_table,file_name):
        load_data_cmd = f"""load data local infile "{file_name}" into table {db_table}"""

        cursor = self.connection.cursor()
        cursor.execute(load_data_cmd)

        cursor.close()

    def execute_query(self,sql_query):

        cursor = self.connection.cursor()
        cursor.execute(sql_query)

        cursor.close()


    def close(self):
        if self.connection != None:
            self.connection.close()
