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


### Usage


#### Rebuilding Your Own




## Example Usage


## Roadmap

- Additional Sources
    - NCBI 
    - Kegg
    - Reactome
        - Pathways
- Pipeline
    - Incremental load (updated records only)
