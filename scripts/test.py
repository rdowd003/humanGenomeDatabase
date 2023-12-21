import os
import pandas as pd

#os.system('./scripts/pull_ncbi_ftp.sh gene_orthologs')

db = "gene_orthologs"
csv_path = f'../data/raw/tmp/{db}.gz'
csv_path = os.path.join(os.path.dirname(__file__), csv_path)
df = pd.read_csv(csv_path,sep='\t')