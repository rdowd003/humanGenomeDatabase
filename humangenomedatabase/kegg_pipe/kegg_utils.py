import pandas as pd
import numpy as np

################################################################################################################
# RAW DATA PROCESSING FUNCTIONS
################################################################################################################

def api_download_to_df(response_data,columns):
    df = pd.DataFrame([x.split('\t') for x in response_data.split('\n')])
    df = df.iloc[:-1,:]
    df.columns = columns
    df.columns = [c.upper() for c in df.columns]

    return df


# Pathways
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
    df['pathway_id'] = df['pathway_id'].apply(lambda x: x.replace('hsa','P'))

    # Drop "Human" description repeated after every name
    df['pathway_name'] = df['pathway_name'].apply(lambda x: x.split(' - ')[0])

    # Save result
    df.columns = [c.upper() for c in df.columns]

    return {'pathway':df}
    

# Genes
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


def process_gene(df):
    df['gene_name'] = df['gene_symbol_and_name'].apply(lambda x: gene_name_split(x))
    df['gene_symbol'] = df['gene_symbol_and_name'].apply(lambda x: gene_symbol_split(x))
    df['gene_id'] = df['gene_id'].apply(lambda x: x.replace('hsa:','G'))

    # Normalize gene-symbol into another look-up table
    gene_symbols = df.explode('gene_symbol')
    gene_symbols = gene_symbols[['gene_symbol','gene_id']]
    # Create a primary key for repeating symbols (where gene_id has > 1 symbol)
    gene_symbols['gene_alias_no'] = gene_symbols.groupby(['gene_id'],as_index=False).cumcount()+1
    gene_symbols.columns = [c.upper() for c in gene_symbols.columns]
    gene_symbols = gene_symbols[['GENE_ID','GENE_SYMBOL','GENE_ALIAS_NO']]

    # Clean up
    df.columns = [c.upper() for c in df.columns]
    df = df.drop(columns=['GENE_SYMBOL','GENE_SYMBOL_AND_NAME'])

    # Note: returns gene table & gene-symbol look up table
    return {'gene':df,'gene_symbol_lookup':gene_symbols}


# Diseases
################################################################################################################

def list_disease_names(disease_row):
    return disease_row.split('; ')

def count_names(disease_row):
    return len(disease_row)

def process_disease(df):
    # Add "DS" to disease_id to match linking-id pattern
    df['disease_id'] = df['disease_id'].apply(lambda x: x.replace('H','DS'))

    # Fix formatting of disease names to match string-list pattern
    df['disease_name'] = df['disease_name'].apply(lambda x: list_disease_names(x))

    # Normalize disease-names into another look-up table
    disease_names = df.explode('disease_name')
    disease_names = disease_names[['disease_id','disease_name']]
    disease_names.columns = [c.upper() for c in disease_names.columns]

    #df = df.groupby(['disease_id'],as_index=False)['disease_name'].count().rename(columns={'disease_name':'disease_name_count'})
    df['disease_name_count'] = df['disease_name'].apply(lambda x: count_names(x))

    df = df.drop(columns=['disease_name'])
    df.columns = [c.upper() for c in df.columns]

    return {'disease':df,'disease_name_lookup':disease_names}
    

# Variants
################################################################################################################

def process_variant(df):
    # Gene variant is related to
    df['variant_version'] = df['variant_id'].apply(lambda x: x.rsplit("v",1)[1])
    df['variant_id'] = df['variant_id'].apply(lambda x: 'V'+x.rsplit("v",1)[0])
    # Gene variant is related to
    df['gene_symbol'] = df['variant_name'].apply(lambda x: x.split(' ')[0])
    df.columns = [c.upper() for c in df.columns]

    return {'variant':df}
    

# Modules
################################################################################################################

def clean_mod_name(mod_row):
    try:
        x = mod_row.rsplit(',',1)[0]
        x = x.replace(' (',',').replace(')','')
        x = x.split(',')
        return x
    
    except:
        return [np.NaN]
    

def process_module(df,return_df=True):
    df['module_name'] = df['module_name'].apply(lambda x: clean_mod_name(x))

    mod_names = df.explode('module_name')
    mod_names.columns = [c.upper() for c in mod_names.columns]

    df['module_name_count'] = df['module_name'].apply(lambda x: count_names(x)) # from disease functions
    df = df.drop(columns=['module_name'])

    df.columns = [c.upper() for c in df.columns]

    return {'module':df,'module_name_lookup':mod_names}
    

# Links
################################################################################################################
def process_link(df,db_table,link_df=pd.DataFrame()):

    if 'pathway_id' in df.columns:
        df['pathway_id'] = df['pathway_id'].apply(lambda x: x.replace('path:hsa','P'))
        df['pathway_id'] = df['pathway_id'].apply(lambda x: x.replace('path:map','P'))

    if 'gene_id' in df.columns:
        df['gene_id'] = df['gene_id'].apply(lambda x: x.replace('hsa:','G'))

    if 'disease_id' in df.columns:
        df['disease_id'] = df['disease_id'].apply(lambda x: x.replace('ds:H','DS'))

    if 'module_id' in df.columns:
        df['module_id'] = df['module_id'].apply(lambda x: x.replace('md:',''))


    if db_table == 'gene_ncbi':
        df['ncbi_gene_id'] = df['ncbi_gene_id'].apply(lambda x: x.replace('ncbi-geneid:','G'))
        df['gene_id'] = df['gene_id'].apply(lambda x: x.replace('hsa:','G'))

    df.columns = [c.upper() for c in df.columns]

    return {db_table:df}


################################################################################################################
# DATABASE PARAMS
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
        
        'proc_func': process_disease
    },
    'variant':{
        'url':'https://rest.kegg.jp/list/variant',
        'columns':['variant_id','variant_name'],
        'proc_func': process_variant
    },
    'module':{
        'url':'https://rest.kegg.jp/list/modul',
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
        'columns':['pathway_id','disease_id']
        #'proc_func': process_link
    },
    'gene_disease':{
        'url':'https://rest.kegg.jp/link/disease/hsa',
        'columns':['disease_id','gene_id']
        #'proc_func': process_link
    },
    'ncbi_gene':{
        'url':'https://rest.kegg.jp/conv/hsa/ncbi-geneid',
        'columns':['ncbi_gene_id','gene_id'],
        'proc_func': process_link
    }
#    'variant_gene_lookup':{
#        'proc_func': process_link_data
#    }
}


valid_dbs = ['pathway','gene','disease','module','variant','pathway_gene','pathway_disease','pathway_module','gene_disease','variant_gene']