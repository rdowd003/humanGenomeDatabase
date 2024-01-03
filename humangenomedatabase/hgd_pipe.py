import os
import pandas as pd
import re

from multiprocessing import Pool
import pyspark.sql.functions as F

from configs import auto_config as cfg
import source_pipes.kegg_pipe.kegg_data_pipe  as kegg
import source_pipes.ncbi_pipe.ncbi_data_pipe as ncbi
import utils.hgd_utils as hgd
import utils.hgd_mysql as hgdm
from utils.hgd_logging import log,get_logger


class humanGenomeDataPipe:
    """
    A class object represents an initialized ETL pipeline for 
    Human-Genome Data. The pipeline can be initialized for one
    of the supported sources (see README).

    ...

    Attributes
    ----------
    pipetype : str
        Required argument, indicating which data-source pipe to initialize
    auto_extract : bool
        Optional argument, indicating whether to re-extract data from source
        or check for existing files in /data/source/raw/ directory
    data_dict: dict
        Non-argument, created on instantiation to store information or data 
        related to data-pipes being worked on
    """
    
    def __init__(self,pipetype="kegg",auto_extract=False):
        self.pipetype = pipetype
        self.data_dict = {"raw":{},"processed":{}}
        self.auto_extract = auto_extract

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
        pipetype : str [required]
            Data source pipeline to instantiate (see read me for
            supported sources)

        Returns
        -------
        None
        """
        
        if pipetype == 'kegg':
            self.datapipe = kegg.keggDataPipe(cfg)

        elif pipetype == 'ncbi':
            self.datapipe = ncbi.ncbiDataPipe(cfg)


    @log
    def validate_db_type(db_table,source_dbs):
        if db_table not in source_dbs:
            raise Exception(f"Invalid Database ({db_table}). Please Try one of: {source_dbs}")


    @log
    def create_database(self,structure_only=False):
        """
        Instantiates a MySQL pipeline to create database
        & related schemas for the Human Genome Database 
        as defined in sql/hgd_database.sql .

        This should be run prior to any "load" function-use
        if loading data into a MySQL database is desired

        Parameters
        ----------
        structure_only : bool [optional]
            Whether to utilize the structure-only backup file
            or the full structure & data backup file. Should be
            set to True for easiest DB set up, with latest 
            published data

        Returns
        -------
        None
        """

        if structure_only:
            file_name = 'hgd_database_structure.sql'
        else:
            file_name = 'hgd_database.sql'

        self.logger.info("Creating database & all schemas for Human Genome Database (human_genome_database)")
        mysqlpipe = hgdm.mysqlDataPipe()
        file_path = f"sql/models/{file_name}.sql"
        mysqlpipe.execute_query(file_path,from_file=True)
        mysqlpipe.close()

    
    ########################################################################################################################################
    ### ETL COMPONENT FUNCTIONS
    ######################################################################################################################################## 
            
    @log
    def extract_table(self,db_table,multi_extract=False):
        """
        Initializes raw data-extraction process for 
        a single data-source dataset.

        Parameters
        ----------
        db_table : str [optional]
            The string-name of the data-source dataset to
            be extracted. See README for valid data sources

        Returns
        -------
        raw_data_dict: dict
            When an extract process is run, regardlless of the db_type,
            a dictionary will always be returned. If the config param 
            "IN_MEM" is True, the dictionary will be {<db_table>:raw_df},
            where the value is the raw extracted data in a pandas
            DataFrame. If "IN_MEM" is False, the raw pandas DF will be saved
            to a flat file and the dict-value will be the file-path instead
            {<db_table>:'path/to/raw/file/filename.csv'}.
        """

        if not multi_extract:
            print(f"Extracting data for database: {db_table}")
            raw_data_dict = self.datapipe.extract_one(db_table)
        else:
            pool = Pool(num_processes=self.ncpu_max)
            raw_data_dict = pool.map(self.datapipe.extract_one,self.datapipe.valid_dbs)
            pool.join()
            pool.close()

        return raw_data_dict
    
    
    @log
    def transform_table(self,db_table,raw_data):
        """
        Initializes raw-data-processing process for 
        a single table.

        Parameters
        ----------
        db_table : str [required]
            The string-name of the data-source dataset to
            be extracted. See README for valid data sources
        raw_data : str OR pandas-dataframe [required]
            Either pandas raw-dataframe ("IN_MEN" = True), or file-paht
            from which the raw_data will be loaded ("IN_MEM" = False)

        Returns
        -------
        proc_data_dict: dict
            When a transform process is run, regardlless of the db_type,
            a dictionary will always be returned. If the config param 
            "IN_MEM" is True, the dictionary will be {<db_table>:proc_df},
            where the value is the processed data in a pandas
            DataFrame. If "IN_MEM" is False, the processed pandas DF will be 
            saved to a flat file and the dict-value will be the file-path instead
            {<db_table>:'path/to/processed/file/filename.csv'}.
        """
        if not cfg.IN_MEM:
            try:
                raw_data = hgd.load_data(db_table,'raw',self.pipetype)
            except:
                raise Exception(f"Table {db_table} not found - please extract first or update data_dict with location of file")

        proc_func = self.datapipe.db_table_dict[db_table]['proc_func']
    
        # All final processing functions return dictionary of {db_table:dataframe}
        # TODO - Find a better way to handle this!! (link processing needs db_table)
        print(f"Processing data for db_table: {db_table}")
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
    def load_table(self,db_table,mysqlpipe,proc_data_df=pd.DataFrame(),overwrite=False):
        """
        Initializes processed-data-loading process for 
        a single table to a database. Data is written to 
        MySQL or SQLlite database

        Parameters
        ----------
        db_table : str [required]
            The string-name of the data-source dataset to
            be extracted. See README for valid data sources
        mysqlpipe : HGD-MySQL object [required]
            Instantiated object fro utils/hgd_mysql - will
            hold connection to DB based on params configured in configy.py
        proc_data_df: Pandas DataFrame [optional]
            The in-memory dataframe to be loaded. If empty or not
            provided, the function will attempt to load the DB table type
            using the utils function. If no table exists or can be loaded,
            there will be an exception.
        overwrite: bool [optional]
            Whether or not to overwrite existing data in MySQL table

        Returns
        -------
        None
        """
        
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
    def single_table_refresh(self,db_table,load_db=False,overwrite=False):
        """
        Initializes full extract-process(-load) "refresh" for a given
        data-source dataset

        Parameters
        ----------
        db_table : str [required]
            The string-name of the data-source dataset to
            be extracted. See README for valid data sources
        mysqlpipe : HGD-MySQL object [required]
            Instantiated object fro utils/hgd_mysql - will
            hold connection to DB based on params configured in configy.py
        proc_data_df: Pandas DataFrame [optional]
            The in-memory dataframe to be loaded. If empty or not
            provided, the function will attempt to load the DB table type
            using the utils function. If no table exists or can be loaded,
            there will be an exception.
        overwrite: bool [optional]
            Whether or not to overwrite existing data in MySQL table

        Returns
        -------
        None
        """

        # Validate table first
        self.validate_db_type(db_table,self.datapipe.db_table_dict)

        # Extract dataset (optionally)
        if self.auto_extract:
            self.data_dict["raw"] = self.extract_table(db_table)
        else:
            # If not re_extract, use what is in raw folder
            raw_path = f'data/raw/{self.pipetype}/'
            onlyfiles = [f for f in os.listdir(raw_path) if os.path.isfile(os.path.join(raw_path, f))]
            file_tpye = '.gz' if db_table in ['gene_info','gene2go','gene_orthologs'] else '.csv'
            pattern = re.compile(fr"{self.pipetype}_human_{re.escape(db_table)}(?:_[a-zA-Z0-9_]+)?\{file_tpye}")
            filtered_filenames = [fn for fn in onlyfiles if pattern.search(fn)]

            if not filtered_filenames:
                self.auto_extract = True
                self.single_table_refresh(db_table,load_db=load_db,overwrite=overwrite)

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
                    self.load_table(db_table,mysqlpipe,proc_data,overwrite)
                else:
                    # Will load data from disk using filepath ("data" will be string)
                    self.load_table(db_table,mysqlpipe,overwrite)

            mysqlpipe.close()
        

    def hgd_refresh(self,db_table_list=[]):
        """
        Initializes full extract-process(-load) "refresh" for a given
        list of data-source datasets. Will call single_table_refresh
        for each table.

        This is similar to a full "main" or "execute" function for 
        a database refresh.

        Parameters
        ----------
        db_table_list : list [optional]
            The string-names of data-source dataset to
            be extracted, processed & loaded. 

        Note: This is intended to be run for one pipetype at
        a time and will not execute for multiple without 
        instantiation of a new humanGenomeDataPipe object

        Returns
        -------
        None
        """

        if not db_table_list:
            db_table_list = list(self.datapipe.db_table_dict.keys())

        for db_table in db_table_list:
            self.data_dict = {"raw":{},"processed":{}}
            self.single_table_refresh(db_table,overwrite=True)


        



        
            


