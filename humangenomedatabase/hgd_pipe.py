import os
import pandas as pd

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from configs import auto_config as cfg
import humangenomedatabase.hgd_utils as hgd
import humangenomedatabase.kegg_pipe  as kegg
import humangenomedatabase.ncbi_pipe as ncbi
import hgd_mysql as hgdm


class humanGenomeDataPipe():
    def __init__(self):
        self.data_dict = {}


    def set_pipe(self,pipetype):
        if pipetype == 'kegg':
            self.datapipe = kegg.keggDataPipe()

        elif pipetype == 'ncbi':
            self.datapipe = ncbi.ncbiDataPipe()
    

    def extract_data(self):

        # If not provided with a db_table, then iterate through all tables for extracting
        if self.db_table:
            raw_data_dict = self.datapipe.extract_one(self.db_table)
        else:
            raw_data_dict = self.datapipe.extract()

        return raw_data_dict


    def transform_data(self):

        # If not provided with a db_table, then iterate through all tables for processing
        if not self.db_table:
            db_table_list = list(self.datapipe.db_table_dict.keys())
        else:
            db_table_list = [self.db_table]
        
        proc_data_dict_all = {}

        for db_table in db_table_list:
            proc_func = self.datapipe.db_table_dict[db_table]['proc_func']

            try:
                data_df = hgd.load_data(self.db_table,self.pipetype,'processed')
            except:
                raise Exception(f"Table {db_table} not found - please extract first")
        
            # All final processing functions return dictionary of {db_table:dataframe}
            proc_data_dict = proc_func(data_df)

            if ((cfg.DEBUG) & (len(db_table_list)==1)):
                return proc_data_dict
            else:
                for db_table,df in proc_data_dict.items():
                    proc_data_dict_all[db_table] = hgd.save_data(df,db_table,self.pipetype)
        
        return proc_data_dict_all



    def load_data(self,data_table_dict):
        
        mysqlpipe = hgdm.mysqlDataPipe()

        for db_table,filepath in data_table_dict.items():
            mysqlpipe.create_table(db_table)
            mysqlpipe.load_data(db_table,filepath)

        mysqlpipe.close()


    def full_etl(self,pipetype):
        self.set_pipe(pipetype)
        self.data_dict["raw"] = self.extract_data()
        self.data_dict["processed"] = self.transform_data()
        self.load_data(self.data_dict["processed"])

    
    def execute(self,pipetype,db_table=None):
        # Sequential run of sources & tables
        
        if not pipetype:
            # Full refresh
            sources_to_run = [source for source in cfg.PIPE_TYPES]
        else:
            # refresh from specific source
            sources_to_run = [self.pipetype]

        # If None, all source-db_tables will refresh, otherwise just the one provided
        self.db_table = db_table
        
        for source in sources_to_run:
            self.full_etl(source)



        



        
            


