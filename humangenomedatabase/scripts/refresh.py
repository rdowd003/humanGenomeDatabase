import argparse
import humangenomedatabase.hgd_pipe as hgdp


# Run full pipeline
parser = argparse.ArgumentParser(description='Human Genome Database Refresher Pipeline')

parser.add_argument('-s','--source',required=True,choices=['kegg','ncbi'],\
                    help="Data source Kegg:('kegg') or NCBI ('ncbi'))")

parser.add_argument('-dbt','--db_tables',required=False,nargs='*',default=None,\
                    help='Kegg or NCBI Database(s) - see README for supported data')

parser.add_argument('-cdb','--create_database',required=False,action='store_true',\
                    help='This flag will instruct creation of Human Genome Database & Schemas for all tables')

args = vars(parser.parse_args())


create_database = args['create_database']
pipetype = args['source']
db_tables = args['db_tables']

# If no source or db_table are given, then it will run a FULL refresh of all sources
hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype=pipetype)

if create_database:
    hgd_pipeline.create_database()

if db_tables:
    hgd_pipeline.hgd_table_refresh(db_tables)

