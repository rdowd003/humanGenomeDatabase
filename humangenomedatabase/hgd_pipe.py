import os
import pandas as pd

from multiprocessing import Pool

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from configs import auto_config as cfg
import humangenomedatabase.hgd_utils as hgd
import humangenomedatabase.kegg_pipe  as kegg
import humangenomedatabase.ncbi_pipe as ncbi
import hgd_mysql as hgdm
from hgd_logging import log


class humanGenomeDataPipe():
    """
    A class object represents an initialized ETL pipeline for 
    Human-Genome Data. The pipeline can be initialized for one
    of the supported sources (see README).

    ...

    Attributes
    ----------
    data_dict : dict
        Stores either the data, or the saved-location of raw and processed 
            data. Can be used with "load_data" utility function, debugging, 
            and simply determining where data is saved during processing 
    full_refresh : bool
        tbd


    Methods
    -------
    set_pipe(pipetype=""):
        Instantiates a source-pipeline class object.
    
    extract_data():
        Initializes raw data-extraction process for 
            either a single table (if db_table argument is
            pass to instantiation) or loop over all tables
            for the given pipetype

            
    tranform_table(db_table):
        Initializes table-specific processing for a given 
            db_table type. Should be used for debugging,
            or when an intermediate output dataframe is 
            desired for a the single table type


    tranform_data(db_table_list):
        Initializes a transformation pipeline process for 
            all given tables


    load_data(overwrite):
        Used to load data to MySQL database & execute queries
        ** Note: different from the utility function by the 
            same name that is used to load csv files into DF

    full_etl():
        Initializes all functions seqentially to create a
            simplified method for running a full-etl for
            the given pipetype, table type, or full-refresh

    execute():
        Initializes the HGD pipe based on parameters given & 
            set via supporting functions
    """
    
    def __init__(self,pipetype="kegg",db_table=None):
        self.pipetype = pipetype
        self.db_table = db_table
        self.data_dict = {"raw":{},"processed":{}}

        # Logging details
        self.log_file_name = cfg.LOG_FILE
        self.logger = log.get_logger(log_file_name=self.log_file_name)

        # Initialize source-pipetype
        self.set_pipe(pipetype)

    ########################################################################################################################################
    ### SETUP FUNCTIONS
    ########################################################################################################################################

    def set_pipe(self,pipetype):
        """
        Instantiates a source-pipeline class object. Mostly 
        used internally, but can be used to instantiate a
        new pipe type (overwriting previous)

        Parameters
        ----------
        pipetype : str
            Data source pipeline to instatiate (see read me for
            supported sources)

        Returns
        -------
        None
        """

        self.logger.info("Initializing {pipetype} pipeline for Human Genome Database")
        
        if pipetype == 'kegg':
            self.datapipe = kegg.keggDataPipe(cfg.DEBUG)

        elif pipetype == 'ncbi':
            self.datapipe = ncbi.ncbiDataPipe(cfg.DEBUG)


    def create_database(self):
        mysqlpipe = hgdm.mysqlDataPipe()
        filepath = "sql/models/hgd_database.sql"
        mysqlpipe.execute_query_file(filepath)
        mysqlpipe.close()

    
    ########################################################################################################################################
    ### ETL COMPONENT FUNCTIONS
    ######################################################################################################################################## 
            
    def extract_table(self,db_table,multi_extract=False):
        if not multi_extract:
            raw_data_dict = self.datapipe.extract_one(self.db_table)
        else:
            pool = Pool(num_processes=self.ncpu_max)
            raw_data_dict = pool.map(self.datapipe.extract_one, self.datapipe.valid_dbs)
            pool.join()
            pool.close()

        return raw_data_dict
    

    def transform_table(self,db_table,raw_data_df=pd.DataFrame()):
        proc_func = self.datapipe.db_table_dict[db_table]['proc_func']

        if raw_data_df.empty:
            try:
                raw_data_df = hgd.load_data(db_table,'raw')
            except:
                raise Exception(f"Table {db_table} not found - please extract first or update data_dict with location of file")
    
        # All final processing functions return dictionary of {db_table:dataframe}
        proc_data_dict = proc_func(raw_data_df)

        if cfg.IN_MEM:
            # Return dataframe for in memory processing
            return proc_data_dict
        
        else:
            # Return filepath metadata for disk-read
            for db_table,proc_data_df in proc_data_dict.items():
                # Replace dataframe with filepath
                proc_data_dict[db_table] = hgd.save_data(proc_data_df,db_table,self.pipetype)
            return proc_data_dict



    def load_table(self,mysqlpipe,db_table,proc_data_df=pd.DataFrame(),overwrite=False):
        if overwrite:
            mysqlpipe.create_table(db_table)

        if proc_data_df.empty:
            try:
                proc_data_df = hgd.load_data(db_table,'processed')
            except:
                raise Exception(f"Table {db_table} not found - please extract first or update data_dict with location of file")
        
        
        mysqlpipe.write_data(db_table,proc_data_df,overwrite)
    

    ########################################################################################################################################
    ### FULL ETL FUNCTIONS
    ######################################################################################################################################## 
    
    
    def single_table_etl(self,db_table,overwrite=False):
        # Extract dataset
        self.data_dict["raw"] = self.extract_table(db_table)

        # Process data
        for db_table,data in self.data_dict["raw"].items():
            # Some "single" tables have multiple outputs
            if cfg.IN_MEM:
                # Data saved in memory, pass to transform function
                self.data_dict["processed"] = self.transform_table(db_table,data)
            else:
                # Will load data from disk using filepath ("data" will be string)
                self.data_dict["processed"] = self.transform_table(db_table)


        # Load processed data to MySQL, sharing connection for all tables
        mysqlpipe = hgdm.mysqlDataPipe()

        for db_table,data in self.data_dict["processed"].items():
            if cfg.IN_MEM:
                self.load_table(mysqlpipe,db_table,data,overwrite)
            else:
                # Will load data from disk using filepath ("data" will be string)
                self.load_table(mysqlpipe,db_table,overwrite)

        mysqlpipe.close()



    def source_refresh(self):
        for db_table in self.datapipe.db_table_dict:
            self.single_table_etl(db_table,overwrite=True)


        



        
            


