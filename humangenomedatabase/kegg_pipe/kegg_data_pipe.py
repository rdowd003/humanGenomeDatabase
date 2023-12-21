import os
from requests_toolbelt.threaded import pool
import requests

import pandas as pd
import numpy as np

import humangenomedatabase.kegg_pipe.kegg_utils as kegg
from humangenomedatabase.hgd_pipe import humanGenomeDataPipe


class keggDataPipe(humanGenomeDataPipe):
    def __init__(self):
        super().__init__()

    def validate_db_type(self):
        if super.db_table not in kegg.valid_dbs:
            raise Exception("Invalid Database. Please Try one of: {valid_dbs}")

    def _extract_one(self,db_table):
        # Get params from dict
        api_url = kegg.db_table_dict[db_table].get('url')
        response = requests.get(api_url)
        data = response.content.decode()

        new_cols = kegg.db_table_dict[db_table].get('columns')
        df = kegg.api_download_to_df(data,new_cols)

        # Save data to local or S3 based on pre-configuration
        super.save_data(df,db_table,'kegg','raw')


    def _extract_all(self):
        # Multi-threaded API calls
        urls_dict = {v['url']:k for k,v in kegg.db_table_dict.items()}
        raw_extract_urls = list(urls_dict.keys())
        p = pool.Pool(num_processes=self.nproc_max).from_urls(raw_extract_urls)
        p.join_all()

        # Save responses as dataframes
        for response in p.responses():
            data = response.content.decode()

            db_table = urls_dict[response.request_kwargs['url']] ####### Need to get the right part of the URL
            new_cols = kegg.db_table_dict[db_table]['columns']

            df = kegg.api_download_to_df(data,new_cols)

            # Save data to local or S3 based on pre-configuration
            super.save_data(df,db_table,'kegg','raw')



    def extract(self):
        if super.db_table:
            raw_data_dict = self._extract_one(super.db_table)
        else:
            raw_data_dict = self._extract_all()



    def _transform_one(self,db_table,data_df):
        
        proc_func = kegg.db_table_dict[db_table]['proc_func']

        if proc_func:
            if data_df.empty:
                data_df = super.load_data(db_table,'kegg','raw')
            
            data_df_dict = proc_func(data_df)

            for db_table,df in data_df_dict.items():
                super.save_data(df,db_table,'kegg','processed')
        
    

    def transform(self,db_table_list=None):

        if not db_table_list:
            db_table_list = kegg.valid_dbs
        
        for db_table in db_table_list:
            self._transform_one(db_table)


    
