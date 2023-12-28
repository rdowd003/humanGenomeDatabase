import os
import requests

import pandas as pd
import numpy as np

import humangenomedatabase.kegg_pipe.kegg_utils as kegg
import humangenomedatabase.hgd_utils as hgd

from multiprocessing import Pool


class keggDataPipe:
    def __init__(self,config):
        self.config = config
        self.db_table_dict = kegg.db_table_dict
        self.valid_dbs = list(self.db_table_dict.keys())


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
        if self.config['IN_MEM']:
            # Return data
            return {db_table:raw_df}
        else:
            # Exchange data for saved filepath
            fp = hgd.save_data(raw_df,db_table,"kegg")
            return {db_table:fp}


        




    



    
