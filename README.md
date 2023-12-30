# humanGenomeDatabase
Repository for data pipeline that will build & update the Human Genome (Analytics) Database

## Overview

### Currently Supported Sources
Below represents a list of currently supported data sources, each with their own respective pipeline. 
Each pipeline has a set of databases that is a sub-section of those from the original genomic source.


| Source    | Database Name  | HGD db_table Name | Extraction Method | Source Link                                                                         |
| ----------| -------------- | ----------------- | ----------------- | ------------------------------------------------------------------------------------
| NCBI      | gene_info      | gene_info         | NCBI FTP          | https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz |
| NCBI      | gene_orthologs | gene_orthologs    | NCBI FTP          | https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_orthologs.gz |
| NCBI      | gene2go        | gene2go           | NCBI FTP          | https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2go.gz |
| NCBI      | gene           | gene_summary      | Entrez/Biopython  | https://www.ncbi.nlm.nih.gov/gene/ |
| NCBI      | snp (dbSNP)    | snp_summary       | Entrez/Biopython  | https://www.ncbi.nlm.nih.gov/snp/ |
| Kegg      | pathway        | pathway           | Kegg API          | https://rest.kegg.jp/list/pathway/hsa/ |
| Kegg      | gene (hsa)     | gene              | Kegg API          | https://rest.kegg.jp/list/hsa/ |
| Kegg      | disease        | disease           | Kegg API          | https://rest.kegg.jp/list/disease/ |
| Kegg      | variant        | variant           | Kegg API          | https://rest.kegg.jp/list/variant/ |
| Kegg      | module         | module            | Kegg API          | https://rest.kegg.jp/list/module/ |

### Source Connectivity & Lookups

**Key**
- Purple: Kegg Datasets (gene, pathway, disease, etc.)
- Blue: Lookup tables for Kegg objects (normalization of Object details such as aliases)
- Green: NCBI Datasets (Gene summary, SNP summary, etc.)
- Yellow: Lookup tables for NCBI objects (normalization of Object details such as aliases)
- Orange: Connection detail demonstrating link between Kegg & NCBI (all can be connected via Genes)
<br>
<br>
![Database Structure](docs/database/hgd_database_diagram.png "Human Genome Database")

### Usage

#### 1. Recreating Database - Using the dump
If you would like to re-create the MySQL database from a backup dump, follow the instructions below.
Note: This is the easiest method, but will result in static data. The pipeline is scheduled to run weekly & upload new dump to 
Github weekly.

Option 1: Initialize Pipeline & Execute Query-file

```
import humangenomedatabase.hgd_pipe as hgdp
hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype='database')

# Structure only
hgd_pipeline.create_database(structure_only=True)

# Full database load with structure & saved data
hgd_pipeline.create_database()
```

Option 2: Load Database From Command-Line

```
# To create database: Start MySQL & sign in
$ mysql -u root -p
    > enter password

# Create database if you haven't already
mysql> CREATE DATABASE human_genome_database;
mysql \q

# Load data from sql-file
$ mysql -p -u [user] human_genome_database < hgd_database.sql
```


#### 2. Recreating Database - Running the pipeline
If you would like to re-create the MySQL database by running the pipeline yourself, follow the instructions below.
Note: This is a trickier method, but will allow you to create your own database & refresh when you want to 

```
# Run 'refresh.py', or use code in your own py-file:
# Initialize pipeline & iterate over sources
for pipetype in ['kegg','ncbi']:
    hgd_pipeline = hgdp.humanGenomeDataPipe(pipetype=pipetype)
    hgd_pipeline.auto_extract = True
    hgd_pipeline.hgd_table_refresh()
```


#### 3. Pulling & Exploring Data without Database
If you are a data scientist, analyst, researcher, or anyone who wants to explore this Human Genome data, follow the steps below
to pull the data locally into your environment





## Roadmap

- Additional Sources
    - NCBI 
    - Kegg
    - Reactome
        - Pathways
- Pipeline
    - Incremental load (updated records only)
