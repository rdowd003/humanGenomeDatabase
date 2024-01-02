import os
import pandas as pd
import numpy as np
import ast

from Bio import Entrez

Entrez.email = os.getenv("ENTREZ_EMAIL")
Entrez.api_key = os.getenv("ENTREZ_API_KEY")

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
    cmd = f'humangenomedatabase/source_pipes/ncbi_pipe/scripts/pull_ncbi_ftp.sh {db_table}'
    os.system(cmd)

    df = pd.read_csv(f'data/raw/ncbi/ncbi_human_{db_table}.gz',sep='\t')
    
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


def batch_fetch_summary_data(db_table,webenv,querykey,record_count,batch_size=5000):
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
def process_ftp_gene(db_table,gene_df,mod_cols={}):
    gene_df.columns = [c.upper() for c in gene_df.columns]

    if gene_df.empty:
        gene_df = pd.read_csv(f"data/raw/tmp/{db_table}.gz",sep="\t")
    
    if db_table in ['snp','gene']:
        new_col_names = {'NAME':'TAX_ID','UID':'GENE_ID'}
    else:
        new_col_names = {'#TAX_ID':'TAX_ID','GENEID':'GENE_ID'}
        if mod_cols:
            new_col_names.update(mod_cols)
        

        gene_df = gene_df.rename(columns=new_col_names)

        gene_df['GENE_ID'] = 'G'+gene_df['GENE_ID'].astype(str)

        # Cut down to human - homo sapien - only
        gene_df = gene_df[gene_df['TAX_ID']==9606].reset_index(drop=True)
        gene_df = gene_df.drop(columns=['TAX_ID'])


    return gene_df


# 2.1.1 Gene Info ##############################################################################################
def split_bar_lists(gi_row):
    return gi_row.split('|')

def normalize_column(df,columns,explode_column):
    df_explode = df.copy(deep=True)
    df_explode = df_explode[columns]
    df_explode = df_explode.explode(explode_column)

    df_explode = df_explode[df_explode[explode_column]!='NaN'].reset_index(drop=True)

    if explode_column == 'SYNONYMS':
        df_explode = df_explode.rename(columns={'SYNONYMS':"GENE_SYMBOL"})

    elif explode_column == 'DBXREFS':
        df_explode['REF_ID'] = df_explode['DBXREFS'].apply(lambda x: x.split(':')[-1])
        df_explode['REF'] = df_explode['DBXREFS'].apply(lambda x: x.split(':')[0].replace(':','_'))
        df_explode = df_explode.drop(columns=[explode_column])

    elif explode_column == 'FEATURE_TYPE':
        df_explode['FEATURE_CAT'] = df_explode['FEATURE_TYPE'].apply(lambda x: x.split(':')[0])
        df_explode['FEATURE'] = df_explode['FEATURE_TYPE'].apply(lambda x: x.split(':')[1])
        df_explode = df_explode.drop(columns=["FEATURE_TYPE"])

    df_explode['LOOKUP_SOURCE'] = 'gene_info'

    return df_explode 


def process_ml_chr(gi_row):
    if gi_row in ['-','Un']:
        return 'Unknown'
    elif gi_row in ['X|Y','XY']:
        return 'X;Y'
    elif '|' in gi_row:
        return  gi_row.replace('|',';')
    else:
        return gi_row
    

def std_gene_type(gi_row):
    if gi_row == 'protein-coding':
        return "CDS"
    elif gi_row == 'unknown':
        return 'Unknown'
    else:
        return gi_row


def process_gene_info(gene_df=pd.DataFrame()):
    mod_cols = {'FULL_NAME_FROM_NOMENCLATURE_AUTHORITY':'NAME','TYPE_OF_GENE':'GENE_TYPE'}
    df = process_ftp_gene("gene_info",gene_df,mod_cols=mod_cols)
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
    df['CHROMOSOME'] = df['CHROMOSOME'].apply(lambda x: process_ml_chr(x))
    df['MAP_LOCATION'] = df['MAP_LOCATION'].apply(lambda x: process_ml_chr(x))
    df['GENE_TYPE'] = df['GENE_TYPE'].apply(lambda x: std_gene_type(x))

    df = df.drop(columns=['SYMBOL'])
    df = df.rename(columns={'SYMBOL_FROM_NOMENCLATURE_AUTHORITY':'GENE_SYMBOL','NAME':'GENE_NAME'})

    final_data = {'gene_info':df,
                  'gene_info_symbol_lookup':explode_dict['SYNONYMS'],
                  'gene_info_dbxref_lookup':explode_dict['DBXREFS'],
                  'gene_info_otherdesig_lookup':explode_dict['OTHER_DESIGNATIONS'],
                  'gene_info_feature_lookup':explode_dict['FEATURE_TYPE']
                }


    return final_data


# 2.1.2 FTP: Gene Orthologs #########################################################################################
def process_gene_orthologs(gene_df=pd.DataFrame()):
    mod_cols = {'OTHER_GENEID':'OTHER_GENE_ID'}
    df = process_ftp_gene("gene_orthologs",gene_df,mod_cols)
    df = df.drop(columns=['RELATIONSHIP'])

    return {'gene_orthologs':df}


# 2.1.3 FTP: Gene2go ###########################################################################################
def process_gene2go(gene_df=pd.DataFrame()):
    mod_cols = {'PUBMED':'PUBMED_ID'}
    df = process_ftp_gene("gene2go",gene_df,mod_cols)
    #df['PUBMED_ID'] = np.where(df['PUBMED_ID']=='-',np.NaN,df['PUBMED_ID'])
    df = df.drop(columns=['PUBMED_ID'])
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
def access_org_tax(gene_row):
    return gene_row['TaxID']

def access_chrom_attr(gene_row,attr='ChrStop'):
    try:
        val = gene_row[0][attr]
    except:
        val = np.NaN
    
    return val

def process_chr(gene_row):
    if gene_row == '':
        return 'Unknown'
    elif gene_row == 'X, Y':
        return 'X;Y'
    elif (not gene_row)|(gene_row == 'Un'):
        return 'Unknown'
    elif ', ' in gene_row:
        return gene_row.replace(', ',';')
    else:
        return gene_row
    

def process_gene_summary(df):
    df = df.rename(columns={'UID':'GENE_ID','MIM':'MIM_ID',
                            'NOMENCLATURENAME':'GENE_NAME',
                            'NAME':'GENE_SYMB_ALT',
                            'GENEWEIGHT':'GENE_WEIGHT',
                            'MAPLOCATION':'MAP_LOCATION'})
    df['GENE_ID'] = 'G'+df['GENE_ID'].astype(str)

    for gi_attr in ['CHRSTART', 'CHRSTOP', 'EXONCOUNT', 'CHRACCVER']:
        df[gi_attr] = df['GENOMICINFO'].apply(lambda x: access_chrom_attr(x,gi_attr))
    
    df['GENE_SYMBOL'] = np.where(df['NOMENCLATURESYMBOL']!='',df['NOMENCLATURESYMBOL'],'')
    df['NOMENCLATURESTATUS'] = np.where(df['NOMENCLATURESTATUS']=='Official',1,0)

    df['GENE_NAME'] = df['GENE_NAME'].replace('',np.NaN)
    df['SUMMARY'] = df['SUMMARY'].replace('',np.NaN)
    df['MAP_LOCATION'] = df['MAP_LOCATION'].replace('',np.NaN)
    df['CHRSTOP'] = df['CHRSTOP'].fillna(0)
    df['CHRSTART'] = df['CHRSTART'].fillna(0)
    df['CHRSTART'] = np.where(df['CHRSTART']==999999999,0,df['CHRSTART'])
    df['CHROMOSOME'] = df['CHROMOSOME'].apply(lambda x: process_chr(str(x)))


    ## Normalize Gene Symbol Aliases
    gene_summary_symbols = df[['GENE_ID','OTHERALIASES']]
    gene_summary_symbols = gene_summary_symbols[gene_summary_symbols['OTHERALIASES']!='']
    gene_summary_symbols = gene_summary_symbols[gene_summary_symbols['OTHERALIASES'].notnull()].reset_index(drop=True)
    gene_summary_symbols['OTHERALIASES'] = gene_summary_symbols['OTHERALIASES'].apply(lambda x: x.split(', '))
    gene_summary_symbols = gene_summary_symbols.explode("OTHERALIASES")
    gene_summary_symbols = gene_summary_symbols.rename(columns={'OTHERALIASES':'GENE_SYMBOL'})

    gene_symb_alt = df[['GENE_ID','GENE_SYMBOL','GENE_SYMB_ALT']]
    gene_symb_alt = gene_symb_alt[gene_symb_alt['GENE_SYMBOL'].notnull()]
    gene_symb_alt['GENE_SYMBOL2'] = gene_symb_alt['GENE_SYMBOL'].apply(lambda x: x.replace('MT-',''))
    gene_symb_alt = gene_symb_alt[gene_symb_alt['GENE_SYMB_ALT']!=gene_symb_alt['GENE_SYMBOL2']].reset_index(drop=True)
    gene_symb_alt = gene_symb_alt.drop(columns=['GENE_SYMBOL','GENE_SYMBOL2'])
    gene_symb_alt = gene_symb_alt.rename(columns={'GENE_SYMB_ALT':'GENE_SYMBOL'})

    gene_summary_symbols = pd.concat([gene_summary_symbols,gene_symb_alt],ignore_index=True)
    gene_summary_symbols['LOOKUP_SOURCE'] = 'gene_summary'

    df['GENE_SYMBOL'] = df['GENE_SYMBOL'].replace('',np.NaN)

    # Normalize Gene-Mim ID Links
    gene_summary_omim = gene_summary_omim.rename(columns={'MIM_ID':'OMIM_ID'})
    gene_summary_omim = gene_summary_omim.explode("OMIM_ID")
    gene_summary_omim = gene_summary_omim[gene_summary_omim['OMIM_ID'].notnull()].reset_index(drop=True)
    gene_summary_omim['LOOKUP_SOURCE'] = 'gene_summary'

    df = df.drop(columns=['LOCATIONHIST','ORGANISM','CHRSORT','OTHERDESIGNATIONS','GENOMICINFO',\
                        'OTHERALIASES','MIM_ID','CHRACCVER','STATUS','CURRENTID','NOMENCLATURESTATUS',
                        'NOMENCLATURESYMBOL','GENE_SYMB_ALT','GENETICSOURCE'])

    gene_data_cols = ['GENE_ID','GENE_SYMBOL'] + [c for c in df.columns if c not in ['GENE_ID','GENE_SYMBOL']]
    df = df[gene_data_cols]
    df.columns = [c.upper() for c in df.columns]

    df = df.sort_values(by=['GENE_ID'])
    df = df.reset_index(drop=True)

    final_data = {'gene_summary':df,
                  'gene_summary_symbol_lookup':gene_summary_symbols,
                  'gene_summary_omim_lookup':gene_summary_omim}

    return final_data


# 2.2.2 SNP Summaries ##########################################################################################
def extract_snp_genes(snp_row):
    snp_row = ast.literal_eval(snp_row)
    return [d['GENE_ID'] for d in snp_row]

def list_attribute(snp_row):
    if pd.isnull(snp_row):
        return np.NaN
    else:
        return snp_row.split(',')

def normalize_snp_column(df,columns,explode_column):
    df_explode = df.copy(deep=True)
    df_explode = df_explode[columns]
    df_explode = df_explode.explode(explode_column)

    df_explode = df_explode[df_explode[explode_column]!='']
    df_explode = df_explode[df_explode[explode_column].notnull()].reset_index(drop=True)
    df_explode['LOOKUP_SOURCE'] = 'snp_summary'

    return df_explode 

def doc_sum_to_dict(snp_row):
    d = {}
    x = snp_row.split('|')

    for i in x:
        isplit = i.split('=')
        d[isplit[0]] = isplit[1]

    return d


def process_snp_summary(df):

    df = df.rename(columns={"GENES":"GENE_ID"})

    df['SNP_ID'] = df['SNP_ID'].apply(lambda x: 'rs'+str(x))
    
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
        'schema_file':'sql/gene_info_schema.sql'
    },
    'gene_orthologs':{
        'proc_func': process_gene_orthologs
    },
    'gene2go':{
        'proc_func': process_gene2go
    },
    'gene_summary':{
        'proc_func': process_gene_summary,
        'search_term':'9606[TID] NOT (replaced[Properties] OR discontinued[Properties]' #) AND officially named[Properties]'
    },
    'snp_summary':{
        'proc_func': process_snp_summary,
        'search_term':'homo sapien[ORGN] AND common variant[Filter] AND snp gene[Filter]'
    }
    #'omim':{
    #    'proc_func': process_omim_summary,
    #    'search_term':'gene[ALL]'
    #}
}