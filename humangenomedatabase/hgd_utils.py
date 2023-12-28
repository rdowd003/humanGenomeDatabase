import os
import pandas as pd
import numpy as np
from configs import auto_config as cfg


def validate_db_type(self,db_table,source_dbs):
    if db_table not in source_dbs:
        raise Exception("Invalid Database. Please Try one of: {source_dbs}")


def load_data(db_table,table_type):
    source = db_table.split('_')[0]
    filename = f"human_{db_table}_data.csv"
    file_path = f"data/{table_type}/{source}/{filename}"

    if cfg.SAVELOC:
        # Load from local dir
        base_dir = os.getcwd()
        return pd.read_csv(os.path.join(base_dir, file_path))
    else:
         # Load from S3
        file_path = file_path.replace('csv','gz')
        bucket = cfg.S3_BUCKET
        s3_filepath = f"s3://{bucket}/{file_path}"
        return pd.read_csv(s3_filepath)


def save_data(self,df,db_table,source,table_type):
    filename = f"human_{db_table}_data.csv"
    file_path = f"data/{table_type}/{source}/{filename}"

    print("Saving file to path: {file_path} in destination: {self.data_location}")
    if cfg.SAVELOC:
        base_dir = os.getcwd()
        file_path = file_path.replace('csv','gz')
        df.to_csv(os.path.join(base_dir, file_path),index=False)
    else:
        bucket = cfg.S3_BUCKET
        s3_filepath = f"s3://{bucket}/{file_path}"
        df.to_csv(s3_filepath,index=False)
    
    return file_path


def join_gene_data(ncbi_gene_info,ncbi_gene_summary,kegg_gene):
    ncbi_gene_info = ncbi_gene_info[['GENE_ID','GENE_TYPE','NOMENCLATURE_STATUS']]
    gene_merged = ncbi_gene_info.merge(ncbi_gene_summary,on=['GENE_ID'],how='outer',suffixes=['_NCBI_GI','_NCBI_SUM'])

    kegg_gene['GENE_ID'] = np.where(kegg_gene['NCBI_GENE_ID'].isnull(),kegg_gene['GENE_ID'],kegg_gene['NCBI_GENE_ID'])
    kegg_gene = kegg_gene.drop(columns=['NCBI_GENE_ID'])
    kegg_gene = kegg_gene[['GENE_ID','CHRSTOP','CHRSTART','CHR_COMPLEMENT','GENE_TYPE']]

    gene_merged = gene_merged.merge(kegg_gene,on=['GENE_ID'],how='outer',suffixes=['','_KEGG'])

    # Post merge processing
    gene_merged['GENE_TYPE'] = np.where(gene_merged['GENE_TYPE'].isnull(),gene_merged['GENE_TYPE_KEGG'],gene_merged['GENE_TYPE'])
    gene_merged['GENE_TYPE_ALT'] = np.where(gene_merged['GENE_TYPE_KEGG']!=gene_merged['GENE_TYPE'],gene_merged['GENE_TYPE_KEGG'],np.NaN)

    gene_merged = gene_merged.drop(columns = ['GENE_TYPE_KEGG','CHRSTOP_KEGG','CHRSTART_KEGG'])

    return gene_merged