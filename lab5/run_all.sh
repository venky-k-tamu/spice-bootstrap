#!/bin/sh
# Run every chain_NN.sp through HSPICE; outputs land in results/chain_NN.*
# Usage (from lab5/, on the HSPICE machine):  sh run_all.sh
set -e
mkdir -p results
for f in chain_*.sp; do
    hspice "$f" -o "results/${f%.sp}" > /dev/null
    echo "done: $f"
done
