if ! [ -x "$(command -v esearch)" ]; then
  echo 'Esearch Command Line Utilities not installed. Installing program now.'
  sh -c "$(curl -fsSL https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"
  export PATH=${HOME}/edirect:${PATH}
else
  echo 'Esearch Utilities already installed!'
  echo "$(command -v esearch)"
fi