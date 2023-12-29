import os
import pandas as pd
import re

from multiprocessing import Pool
import pyspark.sql.functions as F

from humangenomedatabase.configs import auto_config as cfg
import humangenomedatabase.hgd_utils as hgd
import humangenomedatabase.kegg_pipe.kegg_data_pipe  as kegg
import humangenomedatabase.ncbi_pipe.ncbi_data_pipe as ncbi
import humangenomedatabase.hgd_mysql as hgdm
from humangenomedatabase.hgd_logging import log,get_logger


class humanGenomeDataPipe:
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
    
    def __init__(self,pipetype="kegg"):
        self.pipetype = pipetype
        self.data_dict = {"raw":{},"processed":{}}

        # Logging details
        self.log_file_name = 'hgd_pipe_log'
        #self.logger = get_logger(log_file_name=self.log_file_name)

        # Initialize source-pipetype
        self.set_pipe(pipetype)

    ########################################################################################################################################
    ### SETUP FUNCTIONS
    ########################################################################################################################################

    @log
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
        
        if pipetype == 'kegg':
            self.datapipe = kegg.keggDataPipe(cfg)

        elif pipetype == 'ncbi':
            self.datapipe = ncbi.ncbiDataPipe(cfg)


    def create_database(self):
        self.logger.info("Creating database & all schemas for Human Genome Database (human_genome_database)")
        mysqlpipe = hgdm.mysqlDataPipe()
        filepath = "sql/models/hgd_database.sql"
        mysqlpipe.execute_query_file(filepath)
        mysqlpipe.close()

    
    ########################################################################################################################################
    ### ETL COMPONENT FUNCTIONS
    ######################################################################################################################################## 
            
    @log
    def extract_table(self,db_table,multi_extract=False):
        if not multi_extract:
            raw_data_dict = self.datapipe.extract_one(db_table)
        else:
            pool = Pool(num_processes=self.ncpu_max)
            raw_data_dict = pool.map(self.datapipe.extract_one,self.datapipe.valid_dbs)
            pool.join()
            pool.close()

        return raw_data_dict
    
    
    @log
    def transform_table(self,db_table,raw_data):
        if not cfg.IN_MEM:
            try:
                raw_data = hgd.load_data(db_table,'raw',self.pipetype)
            except:
                raise Exception(f"Table {db_table} not found - please extract first or update data_dict with location of file")

        proc_func = self.datapipe.db_table_dict[db_table]['proc_func']
    
        # All final processing functions return dictionary of {db_table:dataframe}
        # TODO - Find a better way to handle this!! (link processing needs db_table)
        if self.datapipe.db_table_dict[db_table]['proc_func'].__name__ == "process_link":
            proc_data_dict = proc_func(raw_data,db_table)
        else:
            proc_data_dict = proc_func(raw_data)

        if cfg.IN_MEM:
            # Return dataframe for in memory processing
            return proc_data_dict
        
        else:
            # Return filepath metadata for disk-read/write
            for db_table,proc_data_df in proc_data_dict.items():
                # Replace dataframe with filepath
                proc_data_dict[db_table] = hgd.save_data(proc_data_df,db_table,source=self.pipetype,table_type="processed")
            return proc_data_dict


    @log
    def load_table(self,mysqlpipe,db_table,proc_data_df=pd.DataFrame(),overwrite=False):
        if overwrite:
            mysqlpipe.create_table(db_table)

        if proc_data_df.empty:
            try:
                proc_data_df = hgd.load_data(db_table,'processed',self.pipetype)
            except:
                raise Exception(f"Table {db_table} not found - please extract first or update data_dict with location of file")
        
        
        mysqlpipe.write_data(db_table,proc_data_df,overwrite)
    

    ########################################################################################################################################
    ### FULL ETL FUNCTIONS
    ######################################################################################################################################## 
    
    @log
    def single_table_refresh(self,db_table,auto_extract=False,load_db=False,overwrite=False):
        # Extract dataset (optionally)
        if auto_extract:
            self.data_dict["raw"] = self.extract_table(db_table)
        else:
            # If not re_extract, use what is in raw folder
            raw_path = f'data/raw/{self.pipetype}/'
            onlyfiles = [f for f in os.listdir(raw_path) if os.path.isfile(os.path.join(raw_path, f))]
            file_tpye = '.gz' if db_table in ['gene_info','gene2go','gene_orthologs'] else '.csv'
            pattern = re.compile(fr"{self.pipetype}_human_{re.escape(db_table)}(?:_[a-zA-Z0-9_]+)?\{file_tpye}")
            filtered_filenames = [fn for fn in onlyfiles if pattern.search(fn)]

            if not filtered_filenames:
                self.single_table_refresh(db_table,auto_extract=True,load_db=load_db,overwrite=overwrite)

            self.data_dict["raw"] = {fn.replace(f'{self.pipetype}_human_','').replace(file_tpye,''):raw_path+fn for fn in filtered_filenames}
        
        # Process data
        for db_table,raw_data in self.data_dict["raw"].items():
            # Some "single" tables have multiple outputs
            self.data_dict["processed"] = self.transform_table(db_table,raw_data)


        if load_db:
            # Load processed data to MySQL, sharing connection for all tables
            mysqlpipe = hgdm.mysqlDataPipe()

            for db_table,proc_data in self.data_dict["processed"].items():
                if cfg.IN_MEM:
                    self.load_table(mysqlpipe,db_table,proc_data,overwrite)
                else:
                    # Will load data from disk using filepath ("data" will be string)
                    self.load_table(mysqlpipe,db_table,overwrite)

            mysqlpipe.close()
        

    def hgd_table_refresh(self,db_table_list=[]):
        if not db_table_list:
            db_table_list = list(self.datapipe.db_table_dict.keys())

        for db_table in db_table_list:
            self.data_dict = {"raw":{},"processed":{}}
            self.single_table_refresh(db_table,overwrite=True)


        



        
            


