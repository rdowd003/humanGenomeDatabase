import humangenomedatabase.hgd_pipe as hgdp
import humangenomedatabase.hgd_mysql as hgdm

import pdb


create_database = False
pipetype = 'ncbi'
#db_tables = ['pathway','gene','module','disease','variant','pathway_gene','pathway_disease','pathway_module','gene_disease']
db_tables = ['gene2go']

# Initialize pipeline
hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype=pipetype)

# Test single table
#data = hgd_pipeline.extract_table('disease')

# Test multiple tables
#hgd_pipeline.hgd_table_refresh(db_tables)

# Load tables to MySQL
db_table = "gene_info"
mysqlpipe = hgdm.mysqlDataPipe()
hgd_pipeline.load_table(mysqlpipe,db_table,overwrite=True)
mysqlpipe.close()

pdb.set_trace()

"""
if create_database:
    hgd_pipeline.create_database()

if db_tables:
    hgd_pipeline.hgd_table_refresh(db_tables)
"""