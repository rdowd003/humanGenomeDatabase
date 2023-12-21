import os
import requests

import pandas as pd

import humangenomedatabase.ncbi_pipe.ncbi_utils as ncbi
from humangenomedatabase.hgd_pipe import humanGenomeDataPipe


class ncbiDataPipe(humanGenomeDataPipe):
    def __init(self):
        super().__init__()
        self.db_table = super.db_table



    def validate_db_type(self):
        if self.db_type not in ncbi.valid_dbs:
            raise Exception("Invalid Database. Please Try one of: {valid_dbs}")



    def _extract_one(self,db_table):
        if db_table in ['gene','snp','omim']:
            db_search_term = ncbi.db_table_dict[db_table]['search_term']
            webenv,querykey,count = ncbi.get_accession_ids(db=db_table,search_term=db_search_term)
            df = ncbi.batch_fetch_summary_data(db=db_table,webenv=webenv,querykey=querykey,record_count=count)

            if db_table == 'gene':
                # Can't figure out why this one won't show up in query above, have to run second time just for this gene
                webenv,querykey,count = ncbi.get_accession_ids(db=db_table,search_term="9606[TID] AND 1[UID]")
                df_1 = ncbi.fetch_data("gene",webenv,querykey)
                df = pd.concat([df_1,df],ignore_index=True)
        else:
            df = ncbi.ftp_script_download(db_table)

        # Save data to local or S3 based on pre-configuration
        super.save_data(df,db_table,'ncbi','raw')



    def _extract_all(self):
        for db_table in ncbi.valid_dbs:
            self._extract_one(db_table,return_df=False)

        # TODO: Create multithreaded version of this like for Kegg



    def extract(self):
        if self.db_table:
            self._extract_one(self.db_table)
        else:
            self._extract_all()

    def transform_one(self):
        pass


    def transform(self):
        pass