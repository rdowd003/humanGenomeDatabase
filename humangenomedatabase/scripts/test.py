import humangenomedatabase.hgd_pipe as hgdp
import humangenomedatabase.utils.hgd_mysql as hgdm

import pdb


create_database = False
pipetype = 'ncbi'
db_tables = ['gene2go']

# Initialize pipeline
hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype=pipetype)
hgd_pipeline.auto_extract = True

# Test multiple tables
hgd_pipeline.hgd_table_refresh(db_tables)
