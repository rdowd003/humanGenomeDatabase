import os
import requests
import pandas as pd

import humangenomedatabase.ncbi_pipe.ncbi_utils as ncbi
import humangenomedatabase.hgd_utils as hgd

from multiprocessing import Pool


class ncbiDataPipe:
    def __init(self,config):
        self.config = config
        self.db_table_dict = self.db_table_dict
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

        if self.config['IN_MEM']:
            return {db_table:raw_df}
        else:
            fp = hgd.save_data(raw_df,db_table,"ncbi")
            return {db_table:fp}


    def load_schema(self,db_table):
        pass