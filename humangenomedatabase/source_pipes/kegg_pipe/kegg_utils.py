import pandas as pd
import numpy as np

################################################################################################################
################################################################################################################
# 1 - KEGG DATA EXTRACTION FUNCTIONS
################################################################################################################
################################################################################################################

def api_download_to_df(response_data,columns):
        df = pd.DataFrame([x.split('\t') for x in response_data.split('\n')])
        df = df.iloc[:-1,:]
        df.columns = columns

        return df

################################################################################################################
################################################################################################################
# 2 - KEGG DATA PROCESSING FUNCTIONS
################################################################################################################
################################################################################################################


################################################################################################################
## 2.1 - Pathways
################################################################################################################

def map_pathway_start(pn_row):
    start = pn_row[0:2]
    if start == "11":
        x = "global_map"
    elif start == "12":
        x = "overview_map"
    elif start == "10":
        x = "chemical_struc_map"
    else:
        if start[0]=="7":
            x = "drug_struc_map"
        else:
            x = "regular_map"

    return x


def process_pathway(df):
    # Add "path:" to pathway_id to match linking -id pattern
    df['PATHWAY_ID'] = df['PATHWAY_ID'].apply(lambda x: x.replace('hsa','P'))

    # Drop "Human" description repeated after every name
    df['PATHWAY_NAME'] = df['PATHWAY_NAME'].apply(lambda x: x.split(' - ')[0])

    return {'pathway':df}
    

################################################################################################################
## 2.2 - Genes
################################################################################################################
def gene_name_split(gene_cf_row):
    try:
        x = gene_cf_row.split(';')[1]
    except:
        x = gene_cf_row.split(';')[0]
    return x


def gene_symbol_split(gene_cf_row):
    col_split = gene_cf_row.split(';')

    if len(col_split)==1:
        x = ['None']
    else:
        x = col_split[0].split(', ')
    return x


def extract_chr_positions(kgene_row,pos_type="start"):
        try:
            if 'complement' in kgene_row:
                kgene_row = kgene_row.split("(")[1].replace(')','')
            else:
                kgene_row = kgene_row.split(":")[1]
            
            if pos_type == "start":
                return int(kgene_row.split('..')[1])
            else:
                return int(kgene_row.split('..')[0])
        except:
            return 0
        

def extract_chr(kgene_row):
    if 'MT' in kgene_row:
        return 'MT'
    elif 'q' in kgene_row:
        return kgene_row.split('q')[0]
    elif ('p' in kgene_row)&('complement' not in kgene_row):
        return kgene_row.split('p')[0]
    elif kgene_row == 'X; Y':
        return 'X;Y'
    elif kgene_row in ['nan','Un','']:
        return 'Unknown'
    elif kgene_row == '13cen':
        return '13'
    else:
        return kgene_row.split(':')[0]


def process_gene(df):
    df['GENE_NAME'] = df['GENE_SYMBOL_AND_NAME'].apply(lambda x: gene_name_split(x))
    df['GENE_SYMBOL'] = df['GENE_SYMBOL_AND_NAME'].apply(lambda x: gene_symbol_split(x))
    df['GENE_ID'] = df['GENE_ID'].apply(lambda x: x.replace('hsa:','G'))

    # Normalize gene-symbol into another look-up table
    gene_symbols = df.explode('GENE_SYMBOL')
    gene_symbols = gene_symbols[['GENE_SYMBOL','GENE_ID']]
    # Create a primary key for repeating symbols (where gene_id has > 1 symbol)
    gene_symbols['gene_alias_no'] = gene_symbols.groupby(['GENE_ID'],as_index=False).cumcount()+1
    gene_symbols.columns = [c.upper() for c in gene_symbols.columns]
    gene_symbols = gene_symbols[['GENE_ID','GENE_SYMBOL','GENE_ALIAS_NO']]
    gene_symbols['LOOKUP_SOURCE'] = 'gene'

    df['CHRSTOP'] = df['CHROMOSOMAL_POSITION'].apply(lambda x: extract_chr_positions(x,pos_type="stop"))
    df['CHRSTART'] = df['CHROMOSOMAL_POSITION'].apply(lambda x: extract_chr_positions(x,pos_type="start"))
    df['CHR_COMPLEMENT'] = np.where(df['CHROMOSOMAL_POSITION'].str.contains('complement'),1,0)
    df['CHROMOSOMAL_POSITION'] = df['CHROMOSOMAL_POSITION'].astype(str)
    df['CHROMOSOME'] = df['CHROMOSOMAL_POSITION'].apply(lambda x: extract_chr(x))

    # Clean up
    df = df.drop(columns=['GENE_SYMBOL','GENE_SYMBOL_AND_NAME','CHROMOSOMAL_POSITION'])

    # Note: returns gene table & gene-symbol look up table
    return {'gene':df,'gene_symbol_lookup':gene_symbols}


################################################################################################################
## 2.3 - Diseases
################################################################################################################

def list_disease_names(disease_row):
    return disease_row.split('; ')

def count_names(disease_row):
    return len(disease_row)

def process_disease(df):
    # Add "DS" to disease_id to match linking-id pattern
    df['DISEASE_ID'] = df['DISEASE_ID'].apply(lambda x: x.replace('H','DS'))

    # Fix formatting of disease names to match string-list pattern
    df['DISEASE_NAME'] = df['DISEASE_NAME'].apply(lambda x: list_disease_names(x))

    # Normalize disease-names into another look-up table
    disease_names = df.explode('DISEASE_NAME')
    disease_names = disease_names[['DISEASE_ID','DISEASE_NAME']]
    disease_names.columns = [c.upper() for c in disease_names.columns]
    disease_names['LOOKUP_SOURCE'] = 'disease'

    #df = df.groupby(['disease_id'],as_index=False)['disease_name'].count().rename(columns={'disease_name':'disease_name_count'})
    df['DISEASE_NAME_COUNT'] = df['DISEASE_NAME'].apply(lambda x: count_names(x))

    df = df.drop(columns=['DISEASE_NAME'])
    df.columns = [c.upper() for c in df.columns]

    return {'disease':df,'disease_name_lookup':disease_names}
    

################################################################################################################
## 2.4 - Variants
################################################################################################################

def process_variant(df):
    # Gene variant is related to
    df['VARIANT_VERSION'] = df['VARIANT_ID'].apply(lambda x: x.rsplit("v",1)[1])
    df['VARIANT_ID'] = df['VARIANT_ID'].apply(lambda x: 'V'+x.rsplit("v",1)[0])
    # Gene variant is related to
    df['GENE_SYMBOL'] = df['VARIANT_NAME'].apply(lambda x: x.split(' ')[0])
    df.columns = [c.upper() for c in df.columns]

    return {'variant':df}
    

################################################################################################################
## 2.5 - Modules
################################################################################################################

def clean_mod_name(mod_row):
    try:
        x = mod_row.rsplit(',',1)[0]
        x = x.replace(' (',',').replace(')','')
        x = x.split(',')
        return x
    
    except:
        return [np.NaN]
    

def process_module(df):
    df['MODULE_NAME'] = df['MODULE_NAME'].apply(lambda x: clean_mod_name(x))

    mod_names = df.explode('MODULE_NAME')
    mod_names.columns = [c.upper() for c in mod_names.columns]
    mod_names['LOOKUP_SOURCE'] = 'module'

    df['MODULE_NAME'] = df['MODULE_NAME'].apply(lambda x: count_names(x)) # from disease functions
    df = df.drop(columns=['MODULE_NAME'])

    df.columns = [c.upper() for c in df.columns]

    return {'module':df,'module_name_lookup':mod_names}
    

################################################################################################################
## 2.6 - Database Links
################################################################################################################

"""
The functions below pull "link" data which demonstrates links or look-ups between two types of Kegg databases.
The tables are named <source>_<target>_lookup. The <source> is used as the priamary table (left) and the
<target> is the joined (right) table. These tables only have the IDs from each link
"""

def process_link(df,db_table):

    if 'PATHWAY_ID' in df.columns:
        df['PATHWAY_ID'] = df['PATHWAY_ID'].apply(lambda x: x.replace('path:hsa','P'))
        df['PATHWAY_ID'] = df['PATHWAY_ID'].apply(lambda x: x.replace('path:map','P'))

    if 'GENE_ID' in df.columns:
        df['GENE_ID'] = df['GENE_ID'].apply(lambda x: x.replace('hsa:','G'))

    if 'DISEASE_ID' in df.columns:
        df['DISEASE_ID'] = df['DISEASE_ID'].apply(lambda x: x.replace('ds:H','DS'))

    if 'MODULE_ID' in df.columns:
        df['MODULE_ID'] = df['MODULE_ID'].apply(lambda x: x.replace('md:',''))


    if db_table == 'gene_ncbi':
        df['NCBI_GENE_ID'] = df['NCBI_GENE_ID'].apply(lambda x: x.replace('ncbi-geneid:','G'))
        df['GENE_ID'] = df['GENE_ID'].apply(lambda x: x.replace('hsa:','G'))

    df.columns = [c.upper() for c in df.columns]

    return {db_table+'_lookup':df}


################################################################################################################
################################################################################################################
# 3 - KEGG DATA PARAMS
################################################################################################################
################################################################################################################

db_table_dict = {
    'pathway':{
        'url':'https://rest.kegg.jp/list/pathway/hsa',
        'columns':['pathway_id','pathway_name'],
        'proc_func': process_pathway
    },
    'gene':{
        'url':'https://rest.kegg.jp/list/hsa',
        'columns':['gene_id','gene_type','chromosomal_position','gene_symbol_and_name'],
        'proc_func': process_gene
    },
    'disease':{
        'url':'https://rest.kegg.jp/list/disease',
        'columns':['disease_id','disease_name'],
        'proc_func': process_disease
    },
    'variant':{
        'url':'https://rest.kegg.jp/list/variant',
        'columns':['variant_id','variant_name'],
        'proc_func': process_variant
    },
    'module':{
        'url':'https://rest.kegg.jp/list/module',
        'columns':['module_id','module_name'],
        'proc_func': process_module
    },
    'pathway_gene':{
        'url':'https://rest.kegg.jp/link/hsa/pathway',
        'columns':['pathway_id','gene_id'],
        'proc_func': process_link
    },
    'pathway_module':{
        'url':'https://rest.kegg.jp/link/module/pathway',
        'columns':['pathway_id','module_id'],
        'proc_func': process_link
    },
    'pathway_disease':{
        'url':'https://rest.kegg.jp/link/disease/pathway',
        'columns':['pathway_id','disease_id'],
        'proc_func': process_link
    },
    'gene_disease':{
        'url':'https://rest.kegg.jp/link/disease/hsa',
        'columns':['disease_id','gene_id'],
        'proc_func': process_link
    },
    'ncbi_gene':{
        'url':'https://rest.kegg.jp/conv/hsa/ncbi-geneid',
        'columns':['ncbi_gene_id','gene_id'],
        'proc_func': process_link
    }
}

