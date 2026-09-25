#!/bin/sh
# Run chain decks through HSPICE; outputs land in results/<deck>.*
# Usage (from lab5/, on the HSPICE machine):
#   sh run_all.sh                      # every chain_*.sp (1 pF and 10 pF)
#   sh run_all.sh 'chain_10pF_*.sp'    # only the 10 pF decks
set -e
mkdir -p results
for f in ${1:-chain_*.sp}; do
    hspice "$f" -o "results/${f%.sp}" > /dev/null
    echo "done: $f"
done
