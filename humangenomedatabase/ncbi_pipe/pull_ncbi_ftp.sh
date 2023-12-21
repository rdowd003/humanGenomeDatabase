#! /bin/zsh

mkdir -p data/raw/ncbi/
mkdir -p data/raw/tmp/ && cd data/raw/

echo "Pulling data for NCBI Entrez DB: $1"

if [[ $1 == "gene_info" ]]
then
    p="GENE_INFO/Mammalia/Homo_sapiens.gene_info"
    #fn="Homo_sapiens.gene_info"
else
    p=$1
    #fn=$1
fi

curl -o tmp/$1.gz https://ftp.ncbi.nlm.nih.gov/gene/DATA/$p.gz

echo pwd

# Unzip file
# not doing this - doing in python instead
#cd tmp/
#gunzip $1.gz && mv $1 ../ncbi/$1.txt


