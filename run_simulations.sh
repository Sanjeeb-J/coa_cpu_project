#!/bin/bash

# Define paths
GEM5_PATH="/home/sanjeeb/gem5/build/X86/gem5.opt"
SIM_SCRIPT="simulate.py"
OUT_DIR="results"

# Create output directory
mkdir -p $OUT_DIR

# Define binaries and CPU models
BINARIES=("matrix_mult" "branch_heavy" "memory_stride")
CPUS=("TimingSimpleCPU" "O3CPU")

# Run simulations
for binary in "${BINARIES[@]}"; do
    for cpu in "${CPUS[@]}"; do
        echo "========================================"
        echo "Running $binary with $cpu"
        echo "========================================"
        
        # Define output directory for this specific run
        RUN_DIR="$OUT_DIR/${binary}_${cpu}"
        
        # Run gem5
        $GEM5_PATH -d $RUN_DIR $SIM_SCRIPT $binary --cpu $cpu
    done
done

echo "All simulations completed!"
