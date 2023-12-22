import os
import pandas as pd
import numpy as np
from Bio import Entrez

from ...configs import auto_config as cfg
Entrez.email = cfg.ENTREZ_EMAIL
Entrez.api_key = cfg.ENTREZ_API_KEY

################################################################################################################
################################################################################################################
# 1 - DATA EXTRACTION FUNCTIONS
################################################################################################################
################################################################################################################

################################################################################################################
## 1.2 NCBI FTP
################################################################################################################

"""
blah blah blah
"""

def ftp_script_download(db_table):
    cmd = f'../scripts/pull_ncbi_ftp.sh {db_table}'
    os.system(cmd)

    df = pd.read_csv(f'data/raw/tmp/{db_table}.gz',sep='\t')

    return df


################################################################################################################
## 1.2 NCBI Entrez
################################################################################################################

"""
blah blah blah
"""

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
################################################################################################################
# 2 - NCBI DATA PROCESSING FUNCTIONS
################################################################################################################
################################################################################################################


################################################################################################################
## 2.1 FTP-DATA PROCESSING
################################################################################################################

"""
The functions below are used on data is that is extracted from NCBI directly via their FTP servers. The data 
is downloaded in compressed-binary format & is saved during the transformation process, ready directly from
the compressed format into pandas dataframes for processing.
"""

# 2.1.0 General Gene-Related ###################################################################################
def process_ftp_gene(db_table,gene_df=pd.DataFrame(),mod_cols={}):

    if gene_df.empty:
        gene_df = pd.read_csv(f"data/raw/tmp/{db_table}.gz",sep="\t")
    
    if db_table in ['snp','gene']:
        new_col_names = {'Name':'tax_id','uid':'Gene_ID'}
    else:
        new_col_names = {'#tax_id':'tax_id','GeneID':'Gene_ID'}
        if mod_cols:
            new_col_names.update(mod_cols)

        gene_df = gene_df.rename(columns=new_col_names)

        gene_df['Gene_ID'] = 'G'+gene_df['Gene_ID'].astype(str)

        # Cut down to human - homo sapien - only
        gene_df = gene_df[gene_df['tax_id']==9606].reset_index(drop=True)
        gene_df = gene_df.drop(columns=['tax_id'])

    gene_df.columns = [c.upper() for c in gene_df.columns]

    return gene_df


# 2.1.1 Gene Info ##############################################################################################
def split_bar_lists(gi_row):
    return gi_row.split('|')

def normalize_column(df,columns,explode_column):
    df_explode = df.copy(deep=True)
    df_explode = df_explode[columns]
    df_explode = df_explode.explode(explode_column)

    df_explode = df_explode[df_explode[explode_column]!='NaN'].reset_index(drop=True)

    if explode_column == 'DBXREFS':
        df_explode['REF_ID'] = df_explode['DBXREFS'].apply(lambda x: x.split(':')[-1])
        df_explode['REF'] = df_explode['DBXREFS'].apply(lambda x: x.split(':')[0].replace(':','_'))
        df_explode = df_explode.drop(columns=[explode_column])

    if explode_column == 'FEATURE_TYPE':
        df_explode['FEATURE_CAT'] = df_explode['FEATURE_TYPE'].apply(lambda x: x.split(':')[0])
        df_explode['FEATURE'] = df_explode['FEATURE_TYPE'].apply(lambda x: x.split(':')[1])
        df_explode = df_explode.drop(columns=["FEATURE_TYPE"])

    return df_explode 


def process_gene_info(mod_cols):
    df = process_ftp_gene(db_table="gene_info",mod_cols=mod_cols)
    df = df.drop(columns=['LOCUSTAG','MODIFICATION_DATE'])

    explode_dict = {}
    exp_cols = ['SYNONYMS','DBXREFS','OTHER_DESIGNATIONS','FEATURE_TYPE']
    for column in exp_cols:
        df[column] = df[column].replace('-','NaN')
        df[column] = df[column].apply(lambda x: split_bar_lists(x))
        exp_cols = ['GENE_ID',column]
        explode_dict[column] = normalize_column(df,exp_cols,column)
    

    df = df.drop(columns=['SYNONYMS','DBXREFS','OTHER_DESIGNATIONS','FEATURE_TYPE'])

    # Binary indicator for official status
    df['NOMENCLATURE_STATUS'] = np.where(df['NOMENCLATURE_STATUS']=='O',1,0)
    df['SYMBOL_FROM_NOMENCLATURE_AUTHORITY'] = np.where(df['SYMBOL_FROM_NOMENCLATURE_AUTHORITY']=='-',df['SYMBOL'],df['SYMBOL_FROM_NOMENCLATURE_AUTHORITY'])
    df['SYMBOL_FROM_NOMENCLATURE_AUTHORITY'] = df['SYMBOL_FROM_NOMENCLATURE_AUTHORITY'].replace('-',np.NaN)
    df['NAME'] = df['NAME'].replace('-',np.NaN)
    df['CHROMOSOME'] = df['CHROMOSOME'].replace('-','Un')

    df = df.drop(columns=['SYMBOL'])
    df = df.rename(columns={'SYMBOL_FROM_NOMENCLATURE_AUTHORITY':'SYMBOL'})

    final_data = {'gene_info':df,
                  'gene_info_synonym_lookup':explode_dict['SYNONYMS'],
                  'gene_info_dbxref_lookup':explode_dict['DBXREFS'],
                  'gene_info_otherdesig_lookup':explode_dict['OTHER_DESIGNATIONS'],
                  'gene_info_feature_lookup':explode_dict['FEATURE_TYPE']
                }


    return final_data


# 2.1.2 FTP: Gene Orthologs #########################################################################################
def process_gene_orthologs(mod_cols):
    df = process_ftp_gene(db_table="gene_orthologs",mod_cols=mod_cols)
    df = df.drop(columns=['RELATIONSHIP'])

    return {'gene_orthologs':df}


# 2.1.3 FTP: Gene2go ###########################################################################################
def process_gene2go(mod_cols):
    df = process_ftp_gene(db_table="gene2go",mod_cols=mod_cols)
    df['PUBMED'] = np.where(df['PUBMED']=='-',np.NaN,df['PUBMED'])
    df['GO_ID'] = df['GO_ID'].apply(lambda x: x.replace(':',''))

    return {'gene2go':df}






################################################################################################################
## 2.2 NCBI Entrez & Biopython
################################################################################################################

"""
The functions below are used on data is that is extracted from NCBI through the use of the python module
"Biopython". This module is a wrapper that relies on the NCBI-developed "Entrez Eutilities" which provide a 
REST api service for querying & extracting all data hosted on the NCBI database servers.
"""

# 2.2.1 Gene Summaries #########################################################################################
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
    df['MapLocation'] = df['MapLocation'].replace('',np.NaN)

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

    final_data = {'gene_summary':df,
                  'gene_summary_symbol_lookup':gene_summary_symbols,
                  'gene_summary_omim_lookup':gene_summary_mim}

    return final_data


# 2.2.2 SNP Summaries ##########################################################################################
def extract_snp_genes(snp_row):
    return [d['GENE_ID'] for d in snp_row]

def list_attribute(snp_row):
    return snp_row.split(',')

def normalize_snp_column(df,columns,explode_column):
    df_explode = df.copy(deep=True)
    df_explode = df_explode[columns]
    df_explode = df_explode.explode(explode_column)

    df_explode = df_explode[df_explode[explode_column]!='']
    df_explode = df_explode[df_explode[explode_column].notnull()].reset_index(drop=True)

    return df_explode 

def doc_sum_to_dict(snp_row):
    d = {}
    x = snp_row.split('|')

    for i in x:
        isplit = i.split('=')
        d[isplit[0]] = isplit[1]

    return d


def process_snp_summary(data):

    df = data.copy(deep=True)
    df = df.rename(columns={"GENES":"GENE_ID"})

    df['SNP_ID'] = 'rs'+df['SNP_ID']
    
    explode_dict = {}
    for column in ['GENE_ID','FXN_CLASS','SS']:
        if column == "GENE_ID":
            df["GENE_ID"] = df["GENE_ID"].apply(lambda x: extract_snp_genes(x))
        else:
            df[column] = df[column].apply(lambda x: list_attribute(x))

        exp_cols = ['SNP_ID',column]
        explode_dict[column] = normalize_snp_column(df,exp_cols,column)


    df['DOCSUM'] = df['DOCSUM'].apply(lambda x: doc_sum_to_dict(x))
    df['SEQ'] = df['DOCSUM'].apply(lambda x: x.get('SEQ'))
    df['LEN'] = df['DOCSUM'].apply(lambda x: x.get('LEN'))
    df['HGVS'] = df['DOCSUM'].apply(lambda x: x.get('HGVS'))

    df['CLINICAL_SIGNIFICANCE'] = df['CLINICAL_SIGNIFICANCE'].replace('',np.NaN)

    drop_cols = ['GLOBAL_SAMPLESIZE','GLOBAL_POPULATION','SUSPECTED',\
                 'ALLELE_ORIGIN','ACC','GLOBAL_MAFS','GENE_LIST','n_genes',\
                 'TAX_ID','CREATEDATE','UPDATEDATE','HANDLE','ORIG_BUILD','CHRPOS_PREV_ASSM','TEXT','uid']
    
    drop_cols = drop_cols + [c for c in df.columns if '_SORT' in c]
    drop_cols += ['GENE_ID','FXN_CLASS','SS','DOCSUM']
    
    for col in drop_cols:
        try:    
            df.drop(columns=[col],inplace=True)
        except:
            pass


    final_data = {'snp_summary':df,
                  'snp_summary_gene_lookup':explode_dict['GENE_ID'],
                  'snp_summary_fxn_lookup':explode_dict['FXN_CLASS'],
                  'snp_summary_ss_lookup':explode_dict['SS']
                }

    return final_data


################################################################################################################
################################################################################################################
# 3 - NCBI DATA PARAMS
################################################################################################################
################################################################################################################
db_table_dict = {
    'gene_info':{
        'proc_func': process_gene_info,
        'mod_cols':{'Full_name_from_nomenclature_authority':'NAME'}
    },
    'gene_orthologs':{
        'proc_func': process_gene_orthologs,
        'mod_cols':{'Other_GeneID':'Other_Gene_ID'}
    },
    'gene2go':{
        'proc_func': process_gene2go,
        'mod_cols':{'PUBMED':'PUBMED_ID'}
    },
    'gene_summary':{
        'proc_func': process_gene_summary,
        'search_term':'9606[TID] NOT (replaced[Properties] OR discontinued[Properties])'
    },
    'snp_summary':{
        'proc_func': process_snp_summary,
        'search_term':'human[ORGN] AND common variant[Filter]'
    },
    #'omim':{
    #    'proc_func': process_omim_summary,
    #    'search_term':'gene[ALL]'
    #}
}