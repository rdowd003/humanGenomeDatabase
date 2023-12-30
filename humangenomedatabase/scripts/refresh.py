import argparse
import humangenomedatabase.hgd_pipe as hgdp


# Run full pipeline
parser = argparse.ArgumentParser(description='Human Genome Database Refresher Pipeline')

parser.add_argument('-s','--sources',required=False,nargs='*',default=[],choices=['kegg','ncbi','database'],\
                    help="Data source Kegg:('kegg') or NCBI ('ncbi'))")

parser.add_argument('-dbt','--db_tables',required=False,nargs='*',default=None,\
                    help='Kegg or NCBI Database(s) - see README for supported data')

parser.add_argument('-cdb','--create_database',required=False,action='store_true',\
                    help='This flag will instruct creation of Human Genome Database & Schemas for all tables')

args = vars(parser.parse_args())


create_database = args['create_database']
pipetypes = args['sources']
db_tables = args['db_tables']


# If no source or db_table are given, then it will run a FULL refresh of all sources
for pipetype in pipetypes:
    hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype=pipetype)
    hgd_pipeline.hgd_table_refresh()

