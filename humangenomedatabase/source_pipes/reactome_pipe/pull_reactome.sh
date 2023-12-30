mkdir -p data/raw/reactome/
curl -o data/raw/reactome/NCBI2Reactome_PE_All_Levels.txt "https://reactome.org/download/current/NCBI2Reactome_PE_All_Levels.txt" # All Pathways
curl -o data/raw/reactome/NCBI2Reactome_PE_Pathway.txt "https://reactome.org/download/current/NCBI2Reactome_PE_Pathway.txt" # Lowest level p-diagram / subset
curl -o data/raw/reactome/NCBI2Reactome_PE_Reactions.txt "https://reactome.org/download/current/NCBI2Reactome_PE_Reactions.txt" # All reactions
curl -o data/raw/reactome/Reactome2OMIM.txt "https://reactome.org/download/current/Reactome2OMIM.txt"
