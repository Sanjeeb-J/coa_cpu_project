# COA CPU Utilization Project: Architectural Analysis using gem5

This project investigates CPU utilization, Instructions Per Cycle (IPC), and Execution Time across different architectural models and cache hierarchies using the cycle-accurate **gem5** simulator.

## Getting Started

### 1. Prerequisites
- **WSL/Ubuntu** environment
- **GCC** for compiling C benchmarks
- **Python 3**
- **gem5** (Installed at `/home/sanjeeb/gem5/build/X86/gem5.opt`)
- **matplotlib** (`pip install matplotlib`)

### 2. Available Workloads
We have developed three distinct C micro-benchmarks targeting different CPU subsystems:
1. `matrix_mult.c`: High compute density, predictable memory access pattern.
2. `branch_heavy.c`: High density of unpredictable branches to stress the branch predictor and pipeline.
3. `memory_stride.c`: Designed to intentionally thrash the L1 Data Cache by striding through a large array.

### 3. Running Simulations
1. Compile the workloads: `make`
2. Run simulations: `./run_simulations.sh`
   *(This script runs each workload on an In-Order CPU `TimingSimpleCPU` and an Out-of-Order CPU `O3CPU`)*

### 4. Extracting Data and Visualizing
- Generate `results_summary.json`: `python3 extract_stats.py`
- Generate PNG charts: `python3 plot_results.py`

### 5. Review Findings
Check out `REPORT.md` for an extensive architectural breakdown and analysis of the generated metrics.
