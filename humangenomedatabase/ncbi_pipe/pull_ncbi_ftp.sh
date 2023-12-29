#! /bin/zsh

mkdir -p data/raw/ncbi/ && cd data/raw/

echo "Pulling data for NCBI Entrez DB: $1"

if [[ $1 == "gene_info" ]]
then
    p="GENE_INFO/Mammalia/Homo_sapiens.gene_info"
    #fn="Homo_sapiens.gene_info"
else
    p=$1
    #fn=$1
fi

curl -o ncbi/ncbi_human_$1.gz https://ftp.ncbi.nlm.nih.gov/gene/DATA/$p.gz

