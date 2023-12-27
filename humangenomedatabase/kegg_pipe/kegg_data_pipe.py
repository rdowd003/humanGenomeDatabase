import os
from requests_toolbelt.threaded import pool
import requests

import pandas as pd
import numpy as np

import humangenomedatabase.kegg_pipe.kegg_utils as kegg
import humangenomedatabase.hgd_utils as hgd


class keggDataPipe():
    def __init__(self,config):
        self.db_table_dict = kegg.db_table_dict
        self.ncpu_max = config['NCPU_MAX']
        self.debug = config['DEBUG']


    def extract_one(self,db_table):
        valid_dbs = list(self.db_table_dict.keys())
        hgd.validate_db_type(db_table,valid_dbs)

        # Get params from dict
        api_url = kegg.db_table_dict[db_table].get('url')
        response = requests.get(api_url)
        data = response.content.decode()

        new_cols = kegg.db_table_dict[db_table].get('columns')
        raw_df = kegg.api_download_to_df(data,new_cols)

        # Return a dictionary of either the data itself (for debugging) or filepath of saved location
        if self.debug:
            # Return data
            raw_df = raw_df.head(100)
            return {db_table:raw_df}
        else:
            # Exchange data for saved filepath
            fp = hgd.save_data(raw_df,db_table,"kegg")
            return {db_table:fp}


    def extract_all(self):
        # Multi-threaded API calls
        urls_dict = {v['url']:k for k,v in self.db_table_dict.items()}
        raw_extract_urls = list(urls_dict.keys())
        p = pool.Pool(num_processes=self.ncpu_max).from_urls(raw_extract_urls)
        p.join_all()

        extract_data_dict = {}

        # Extract data into dataframes & add file-paths of each saved DF to filepath-dicitonary
        # No returning data - this is intended to be looping over all DBs
        for response in p.responses():
            try:
                data = response.content.decode()

                db_table = urls_dict[response.request_kwargs['url']] ####### Need to get the right part of the URL
                new_cols = self.db_table_dict[db_table]['columns']

                raw_df = kegg.api_download_to_df(data,new_cols)
                extract_data_dict[db_table] = hgd.save_data(raw_df,db_table,"kegg")
            except:
                pass

        return extract_data_dict

        




    



    
