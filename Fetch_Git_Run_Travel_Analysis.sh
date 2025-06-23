#!/usr/bin/bash
 # Download the scripts
gith="https://raw.githubusercontent.com/sustance/iataBoardPass/refs/heads/main/"

# Start ssh-agent if not running
if [ -z "$SSH_AUTH_SOCK" ]; then
    eval "$(ssh-agent -s)"
fi

# Add your key to the agent (will prompt for passphrase once)
ssh-add ~/.ssh/id_ed25519  # or whatever your private key is named

# THIS FAILS UNLESS THE DIRECTORY IS EMPTY
rm $HOME/tmp/*
git clone git@github.com:sustance/pdata.git $HOME/tmp/pdata/
# passphrase is "kym.michael@gmail.com" perhaps need to do manually once per session
 
/bin/curl \
https://raw.githubusercontent.com/sustance/iataBoardPass/refs/heads/main/Flight_Data_Processing.py \
-o $HOME/tmp/Flight_Data_Processing.py


 # Check if YEAR is set
 if [ -z "$YEAR" ]; then
     echo "Error: YEAR environment variable not set."
     echo "Usage: $YEAR bpScanList.sh"
     exit
 fi
 
 YEAR_FILE="IATA_BP_Scans_${YEAR}raw.csv"
 echo "Working on Year $YEAR ..."

YEAR=${YEAR} cat ${HOME}/tmp/pdata/IATA_BP_Scans_2025 | python3 $HOME/tmp/scansRawToCompact.py

