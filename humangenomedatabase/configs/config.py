
import os

class Common(object):
    NCPU_MAX = 1
    SOURCES = ['kegg','ncbi']

    LOG_FILE = 'hgd_pipeline'
    
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    S3_BUCKET = "human-genome-data/database"

class Local(Common):
    IN_MEM = False
    LOG_DIR = "local/"
    SAVELOC = False

    RDS_DB = "human-genome-database"
    DB_USER = os.getenv('HGD_USER')
    DB_PASS = os.getenv('HGD_PASSWORD')
    DB_HOST = "localhost"


class Production(Common):
    IN_MEM = True
    LOG_DIR = "production/"
    SAVELOC = False

    RDS_DB = "human-genome-database-dev1"
    DB_USER = os.getenv('HGD_USER')
    DB_PASS = os.getenv('HGD_PASSWORD')
    DB_HOST = os.getenv('HCG_HOST')


class Staging(Production):
    IN_MEM = True