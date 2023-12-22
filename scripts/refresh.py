import argparse
import humangenomedatabase.hgd_pipe as hgdp


# Set up full pipeline manually - single source
"""
hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype="kegg",db_table="gene")
data_dict = {}
data_dict["raw"] = hgd_pipeline.extract_data()
data_dict["processed"] = hgd_pipeline.transform_data()
hgd_pipeline.load_data(data_dict["processed"])
"""

# Run full pipeline
parser = argparse.ArgumentParser(description='Human Genome Database Refresher Pipeline')
parser.add_argument('-s','--source', help="Data source Kegg:('kegg') or NCBI ('ncbi'))", required=False)
parser.add_argument('-db','--db_table', help='Kegg or NCBI Database - see README for supported data', required=False)
args = vars(parser.parse_args())


pipetype = args['source']
db_table = args['db_table']

# If no source or db_table are given, then it will run a FULL refresh of all sources
hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype=pipetype,db_table=db_table)
hgd_pipeline.execute()

