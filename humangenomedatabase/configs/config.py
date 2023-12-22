
import os

class Common(object):
    NCPU_MAX = 1
    SOURCES = ['kegg','ncbi']
    
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    S3_PATH = "human-genome-data/database/"

class Local(Common):
    SAVELOC = True
    RDS_DB = "human-genome-database-dev1"
    DEBUG = True
    DB_USER = os.getenv('HGD_USER')
    DB_PASS = os.getenv('HGD_PASSWORD')
    DB_HOST = "localhost"

class Production(Common):
    SAVELOC = False
    RDS_DB = "human-genome-database-dev1"
    DEBUG = False
    DB_USER = os.getenv('HGD_USER')
    DB_PASS = os.getenv('HGD_PASSWORD')
    DB_HOST = os.getenv('HCG_HOST')


class Staging(Production):
    DEBUG = True
