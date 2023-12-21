import os
import pandas as pd

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from ..configs import auto_config as cfg


class humanGenomeDataPipe:
    def __init__(self,data_location='local',db_table=None):
        super().__init__()
        self.data_location = data_location
        self.db_table = db_table
        self.data_loc_dict = {}

    def start_spark_session(self):
        self.spark = SparkSession.builder.master("local[{cfg.NCPU_MAX}]").appName("HGD_PIPE").getOrCreate()


    def load_data(self,db_table,source,table_type):
        filename = f"human_{db_table}_data.csv"
        file_path = f"data/{table_type}/{source}/{filename}"

        if self.data_location == 's3':
            bucket = cfg.S3_BUCKET
            s3_filepath = f"s3://{bucket}/{file_path}"
            return pd.read_csv(s3_filepath)
        
        else:
            base_dir = os.getcwd()
            return pd.read_csv(os.path.join(base_dir, file_path))


    def save_data(self,df,db_table,source,table_type):
        filename = f"human_{db_table}_data.csv"
        file_path = f"data/{table_type}/{source}/{filename}"

        print("Saving file to path: {file_path} in destination: {self.data_location}")
        if self.data_location == 's3':
            bucket = cfg.S3_BUCKET
            s3_filepath = f"s3://{bucket}/{file_path}"
            df.to_csv(s3_filepath,index=False)
        else:
            base_dir = os.getcwd()
            df.to_csv(os.path.join(base_dir, file_path),index=False)

        # For debugging
        self.data_loc_dict[db_table] = f"({self.data_location}){file_path}"


    def load_data_mysql(self,df):
        db_user = os.getenv('HGD_USER')
        db_pass = os.getenv('HGD_PASSWORD')
        db_host = os.getenv('HCG_HOST')


    def stop_spark_session(self):
        self.spark.stop()


