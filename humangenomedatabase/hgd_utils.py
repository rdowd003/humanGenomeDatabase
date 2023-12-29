import os
import pandas as pd
import numpy as np
from pathlib import Path

from humangenomedatabase.configs import auto_config as cfg


def validate_db_type(db_table,source_dbs):
    if db_table not in source_dbs:
        raise Exception(f"Invalid Database ({db_table}). Please Try one of: {source_dbs}")


def load_data(db_table,table_type,source):
    filename = f"{source}_human_{db_table}.csv"
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


def save_data(df,db_table,source,table_type,compressed=False):
    file_name = f"{source}_human_{db_table}.csv"
    file_path = f"data/{table_type}/{source}/"

    if compressed:
        file_path = file_path.replace('csv','gz')

    print(f"Saving file to path: {file_path}")
    if cfg.SAVELOC:
        Path(file_path).mkdir(parents=True, exist_ok=True)
        file_path += file_name
        base_dir = os.getcwd()
        df.to_csv(os.path.join(base_dir, file_path),index=False)
    else:
        file_path += file_name
        bucket = cfg.S3_BUCKET
        s3_filepath = f"s3://{bucket}/{file_path}"
        df.to_csv(s3_filepath,index=False)
    
    return file_path


"""
This will be added as Stored Procedure to DB, not done in python - saving to remember details of transformations
"""
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