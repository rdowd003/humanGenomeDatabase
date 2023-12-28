import os
import pandas as pd

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from configs import auto_config as cfg
import humangenomedatabase.hgd_utils as hgd
import humangenomedatabase.kegg_pipe  as kegg
import humangenomedatabase.ncbi_pipe as ncbi
import hgd_mysql as hgdm
from hgd_logging import log

class humanGenomeDataPipe():
    def __init__(self):
        self.data_dict = {}
        self.full_refresh = False

        # Logging details
        self.log_file_name = cfg.LOG_FILE
        self.logger = log.get_logger(log_file_name=self.log_file_name)


    def set_pipe(self,pipetype):
        self.logger.info("Initializing {pipetype} pipeline for Human Genome Database")
        
        if pipetype == 'kegg':
            self.datapipe = kegg.keggDataPipe(cfg.DEBUG)

        elif pipetype == 'ncbi':
            self.datapipe = ncbi.ncbiDataPipe(cfg.DEBUG)
    

    def extract_data(self):

        # If not provided with a db_table, then iterate through all tables for extracting
        if self.db_table:
            raw_data_dict = self.datapipe.extract_one(self.db_table)
        else:
            raw_data_dict = self.datapipe.extract_all()

        return raw_data_dict
    

    def transform_table(self,db_table):
        proc_func = self.datapipe.db_table_dict[db_table]['proc_func']

        try:
            data_df = hgd.load_data(db_table,self.pipetype,'processed')
        except:
            raise Exception(f"Table {db_table} not found - please extract first")
    
        # All final processing functions return dictionary of {db_table:dataframe}
        proc_data_dict = proc_func(data_df)

        if cfg.DEBUG:
            return proc_data_dict
        else:
            self.data_dict["processed"][db_table] = hgd.save_data(data_df,db_table,self.pipetype)


    def transform_data(self,db_table_list=None):

        # If not provided with a db_table, then iterate through all tables for processing
        if not db_table_list:
            db_table_list = list(self.datapipe.db_table_dict.keys())

        for db_table in db_table_list:
            self.transform_table(db_table)


    def load_data(self):

        mysqlpipe = hgdm.mysqlDataPipe()
        table_list = self.data_dict["processed"].items()

        for db_table,filepath in table_list:
            mysqlpipe.create_table(db_table)
            mysqlpipe.load_data(db_table,filepath)

        mysqlpipe.close()



    def full_etl(self,pipetype):
        self.set_pipe(pipetype)
        self.data_dict["raw"] = self.extract_data()
        self.data_dict["processed"] = self.transform_data()
        self.load_data()


    
    def execute(self,pipetype,db_table=None):
        # Sequential run of sources & tables
        # If db_table=None, all source-db_tables will refresh, otherwise just the one provided
        self.pipetype = pipetype
        self.db_table = db_table
        
        if pipetype == 'refresh':
            # Full refresh
            sources_to_run = [source for source in cfg.SOURCES]
        else:
            # refresh from specific source
            sources_to_run = [self.pipetype]
        
        for source in sources_to_run:
            self.full_etl(source)

        



        
            


