import os
import requests
import pandas as pd

import humangenomedatabase.ncbi_pipe.ncbi_utils as ncbi
import humangenomedatabase.hgd_utils as hgd

from multiprocessing import Pool


class ncbiDataPipe:
    def __init(self,config):
        self.db_table_dict = self.db_table_dict
        self.debug = config['DEBUG']
        self.valid_dbs = list(self.db_table_dict.keys())
    
    def extract_one(self,db_table):
        hgd.validate_db_type(db_table,self.valid_dbs)

        if db_table in ['gene_summary','snp_summary']:
            db_search_term = self.db_table_dict[db_table]['search_term']
            ncbi_db = db_table.replace('_summary','')
            webenv,querykey,count = ncbi.get_accession_ids(db=ncbi_db,search_term=db_search_term)
            raw_df = ncbi.batch_fetch_summary_data(db=ncbi_db,webenv=webenv,querykey=querykey,record_count=count)
        else:
            raw_df = ncbi.ftp_script_download(db_table)

        if self.debug:
            raw_df = raw_df.head(100)
            return {db_table:raw_df}
        else:
            fp = hgd.save_data(raw_df,db_table,"ncbi")
            return {db_table:fp}


    def extract_all(self):
        """
        extract_data_dict = {}

        for db_table in ncbi.valid_dbs:
            extract_data_dict.update(self.extract_one(db_table))
        """

        pool = Pool(num_processes=self.ncpu_max)
        results = pool.map(self.extract_one, self.valid_dbs)
        pool.join()
        pool.close()

        extract_data_dict = {}
        for data_dict in results:
            for db_table,df in data_dict.items():
                fp = hgd.save_data(df,db_table,"ncbi","raw")
                extract_data_dict[db_table] = fp

        return extract_data_dict

        