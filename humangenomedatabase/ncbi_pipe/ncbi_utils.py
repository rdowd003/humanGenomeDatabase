import os
import pandas as pd
import numpy as np
from Bio import Entrez

from ...configs import auto_config as cfg
Entrez.email = cfg.ENTREZ_EMAIL
Entrez.api_key = cfg.ENTREZ_API_KEY

################################################################################################################
# RAW DATA EXTRACT FUNCTIONS
################################################################################################################

# NCBI-FTP-Related Extraction Functions
################################################################################################################
def ftp_script_download(db_table):
    cmd = f'../scripts/pull_ncbi_ftp.sh {db_table}'
    os.system(cmd)

    df = pd.read_csv(f'data/raw/tmp/{db_table}.gz',sep='\t')

    return df


# Entrez-Related Extraction Functions
################################################################################################################
def get_db_fields(db_table="gene",verbose=False):
    handle = Entrez.einfo(db=db_table)
    record = Entrez.read(handle)
    data = list(record["DbInfo"]["FieldList"])
    data = pd.DataFrame(data)

    if verbose:
        print(data)

    return data


def get_accession_ids(db_table,search_term,retmax=None,usehistory='y'):
    """Use ESearch to get list of AccessionIds for search
    """
    esearch_handle = Entrez.esearch(db=db_table,retmax=retmax,term=search_term,usehistory=usehistory,idtype="acc")
    records = Entrez.read(esearch_handle)
    esearch_handle.close()

    if usehistory == 'y':
        return records['WebEnv'],records['QueryKey'],int(records["Count"])
    else:
        return records['IdList']


def extract_record_uid(entrez_dictelement):
    raw_data = entrez_dictelement
    record = dict(raw_data.items())
    uid = raw_data.attributes
    record.update(uid)
    return record


def fetch_data(db_table,webenv,querykey,
               batch_size=10,retstart=0,rettype=None,retmode="xml"):
    """Fetch Entrez Gene records using Bio.Entrez, in particular epost
    (to submit the data to NCBI) and efetch to retrieve the
    information, then use Entrez.read to parse the data.

    Returns a list of parsed gene records.
    """

    efetch_result = Entrez.esummary(db=db_table,
                                    webenv=webenv,
                                    retstart=retstart,
                                    retmax=batch_size,
                                    query_key=querykey,
                                    rettype=rettype,
                                    retmode=retmode)
    records = Entrez.read(efetch_result)
    efetch_result.close()

    raw_records = records['DocumentSummarySet']['DocumentSummary']
    final_data = [extract_record_uid(d) for d in raw_records]
    records = pd.DataFrame(final_data)

    return records


def batch_fetch_summary_data(db_table,webenv,querykey,record_count,batch_size=100000):
    final_data = pd.DataFrame()
    for start in range(0, record_count, batch_size):

        end = min(record_count, start + batch_size)
        fetched_data = fetch_data(db_table,webenv,querykey,retstart=start,batch_size=batch_size)
        final_data = pd.concat([final_data,fetched_data],ignore_index=True)
    
    return final_data


################################################################################################################
# RAW DATA PROCESSING FUNCTIONS
################################################################################################################

# Gene-Related General - Usd on FTP-downloads & Entrez Extractions
################################################################################################################
def process_gene_general(gene_df=pd.DataFrame(),db_table=None):

    if gene_df.empty:
        gene_df = pd.read_csv(f"data/raw/tmp/{db_table}.gz",sep="\t")
    
    if db_table in ['snp','gene']:
        columns = {'Name':'tax_id','uid':'Gene_ID'}
    else:
        columns = {'#tax_id':'tax_id','GeneID':'Gene_ID'}
        gene_df = gene_df.rename(columns={'#tax_id':'tax_id','GeneID':'Gene_ID'})
        gene_df = gene_df[gene_df['tax_id']==9606].reset_index(drop=True)

    gene_df.columns = [c.upper() for c in gene_df.columns]

    return gene_df


# FTP: Gene Info
################################################################################################################
def process_gene_info(df):
    df = process_gene_general(df)
    df = df.drop(columns=['TAX_ID','LOCUSTAG','MODIFICATION_DATE','DBXREFS'])

    return {'gene_info':df}


# FTP: Gene Orthologs
################################################################################################################
def process_gene_orthologs(df):
    df = process_gene_general(df)
    df = df.rename(columns={'OTHER_GENEID':'OTHER_GENE_ID'})
    df = df.drop(columns=['TAX_ID','RELATIONSHIP'])

    return {'gene_orthologs':df}


# FTP: Gene2Go
################################################################################################################
def process_gene2go(df):
    df = process_gene_general(df)
    df = df.rename(columns={'PUBMED':'PUBMED_ID'})
    df = df.drop(columns=['TAX_ID'])

    return {'gene2go':df}


# Entrez: Gene Summaries
################################################################################################################
def access_org_tax(org_row):
    return org_row['TaxID']

def access_chrom_attr(genomic_info_row,attr='ChrStop'):
    try:
        val = genomic_info_row[0][attr]
    except:
        val = np.NaN
    
    return val

def process_gene_summary(df):
    df = df.rename(columns={'uid':'GENE_ID','Mim':'MIM_ID'})

    # Cut genes down to official genes
    df = df[(df['CurrentID']=='0')&(df['Status']=='0')].reset_index(drop=True)

    for gi_attr in ['ChrStop','ExonCount','ChrAccVer']:
        df[gi_attr] = df['GenomicInfo'].apply(lambda x: access_chrom_attr(x,gi_attr))
    
    df['GENE_SYMBOL'] = np.where(df['NomenclatureSymbol']!='',df['NomenclatureSymbol'],df['Name'])
    df['NomenclatureStatus'] = np.where(df['NomenclatureStatus']=='Official',1,0)

    df['NomenclatureSymbol'] = df['NomenclatureSymbol'].replace('',np.NaN)
    df['NomenclatureName'] = df['NomenclatureName'].replace('',np.NaN)
    df['Summary'] = df['Summary'].replace('',np.NaN)

    ## Normalize Gene Symbol Aliases
    gene_summary_symbols = df[['GENE_ID','OtherAliases']]
    gene_summary_symbols = gene_summary_symbols[gene_summary_symbols['OtherAliases']!=''].reset_index(drop=True)
    gene_summary_symbols['OtherAliases'] = gene_summary_symbols['OtherAliases'].apply(lambda x: x.split(', '))
    gene_summary_symbols = gene_summary_symbols.explode("OtherAliases")
    gene_summary_symbols = gene_summary_symbols.rename(columns={'OtherAliases':'GENE_SYMBOL'})

    # Normalize Gene-Mim ID Links
    gene_summary_mim = df[['GENE_ID','MIM_ID']]
    gene_summary_mim = gene_summary_mim.explode("MIM_ID")
    gene_summary_mim = gene_summary_mim[gene_summary_mim['MIM_ID'].notnull()].reset_index(drop=True)

    df = df.drop(columns=['LocationHist','Organism','ChrSort','OtherDesignations','GenomicInfo','OtherAliases','MIM_ID','ChrAccVer','Name','Status','CurrentID'])

    gene_data_cols = ['GENE_ID','GENE_SYMBOL'] + [c for c in df.columns if c not in ['GENE_ID','GENE_SYMBOL']]
    df = df[gene_data_cols]
    df.columns = [c.upper() for c in df.columns]

    return {'gene_summary':df,'gene_symbol_lookup':gene_summary_symbols,'gene_omim_lookup':gene_summary_mim}


# Entrez: SNP Summaries
################################################################################################################
def process_snp_summary(df):
    webenv,querykey,count = get_accession_ids(db="snp",search_term="human[ORGN]")
    df = batch_fetch_summary_data(db="snp",webenv=webenv,querykey=querykey,record_count=count)

    return {'snp':df}


################################################################################################################
# DATABASE PARAMS
################################################################################################################
db_table_dict = {
    'gene_info':{
        'proc_func': process_gene_info
    },
    'gene_orthologs':{
        'proc_func': process_gene_orthologs
    },
    'gene2go':{
        'proc_func': process_gene2go
    },
    'gene':{
        'proc_func': process_gene_summary,
        'search_term':'9606[TID] NOT (replaced[Properties] OR discontinued[Properties])'
    },
    'snp':{
        'proc_func': process_snp_summary,
        'search_term':'human[ORGN]'
    },
    'omim':{
        'proc_func': process_omim_summary,
        'search_term':'gene[ALL]'
    }
}

valid_dbs = ['gene','snp','omim','gene_info','gene2go','gene_orthologs']