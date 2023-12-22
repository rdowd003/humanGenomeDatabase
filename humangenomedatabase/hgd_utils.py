import os
import pandas as pd
from configs import auto_config as cfg


def validate_db_type(self,db_table,source_dbs):
    if db_table not in source_dbs:
        raise Exception("Invalid Database. Please Try one of: {source_dbs}")


def load_data(db_table,source,table_type):
    filename = f"human_{db_table}_data.csv"
    file_path = f"data/{table_type}/{source}/{filename}"

    if cfg.SAVELOC:
        # Load from local dir
        base_dir = os.getcwd()
        return pd.read_csv(os.path.join(base_dir, file_path))
    else:
         # Load from S3
        bucket = cfg.S3_BUCKET
        s3_filepath = f"s3://{bucket}/{file_path}"
        return pd.read_csv(s3_filepath)


def save_data(self,df,db_table,source,table_type):
    filename = f"human_{db_table}_data.csv"
    file_path = f"data/{table_type}/{source}/{filename}"

    print("Saving file to path: {file_path} in destination: {self.data_location}")
    if cfg.SAVELOC:
        base_dir = os.getcwd()
        df.to_csv(os.path.join(base_dir, file_path),index=False)
    else:
        bucket = cfg.S3_BUCKET
        s3_filepath = f"s3://{bucket}/{file_path}"
        df.to_csv(s3_filepath,index=False)
    
    return file_path