
import os

class Common(object):
    NCPU_MAX = 1
    SOURCES = ['kegg','ncbi']

    LOG_FILE = 'hgd_pipeline'
    
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    S3_BUCKET = "human-genome-data/database"

class Local(Common):
    IN_MEM = True
    LOG_DIR = "local/"
    SAVELOC = True

    RDS_DB = "human-genome-database"


class Production(Common):
    IN_MEM = True
    LOG_DIR = "production/"
    SAVELOC = False

    RDS_DB = "human-genome-database-dev1"
    DB_USER = os.getenv('HGD_USER_RDS')
    DB_PASS = os.getenv('HGD_PASSWORD_RDS')
    DB_HOST = os.getenv('HCG_HOST_RDS')


class Staging(Production):
    IN_MEM = True
    DB_USER = os.getenv('HGD_USER_LOC')
    DB_PASS = os.getenv('HGD_PASSWORD_LOC')
    DB_HOST = "localhost"