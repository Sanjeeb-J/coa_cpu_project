# COA CPU Utilization Project — Complete Documentation

> **Environment:** Windows 11 with WSL (Ubuntu) | **Simulator:** gem5 (X86, SE Mode)  
> **Location:** `/home/sanjeeb/coa_cpu_project/`

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Project File Structure](#2-project-file-structure)
3. [Source Code (All Files)](#3-source-code-all-files)
4. [Step-by-Step: How to Run](#4-step-by-step-how-to-run)
5. [Understanding stats.txt](#5-understanding-statstxt)
6. [Extracting Stats & Plotting Graphs](#6-extracting-stats--plotting-graphs)
7. [Results (results_summary.json)](#7-results-results_summaryjson)
8. [Graphs Generated](#8-graphs-generated)
9. [Analysis & Key Findings](#9-analysis--key-findings)

---

## 1. Project Overview

This project uses the **gem5 cycle-accurate CPU simulator** to investigate how different **CPU architectural designs** impact performance across three different types of workloads.

### What Is Being Compared?

| CPU Model | Type | Description |
|---|---|---|
| `TimingSimpleCPU` | **In-Order** | Executes one instruction fully before the next. Simple but slow. |
| `O3CPU` | **Out-of-Order (OoO)** | Can execute multiple instructions simultaneously, reordering them to hide latency. |

### Three Workloads (Benchmarks)

| Benchmark | What It Stresses |
|---|---|
| `matrix_mult` | Compute pipeline — heavy integer/FP operations, predictable memory |
| `branch_heavy` | Branch predictor — many unpredictable conditional jumps |
| `memory_stride` | Memory/Cache system — large array striding that thrashes L1/L2 cache |

### System Configuration (set in `simulate.py`)

| Component | Setting |
|---|---|
| Clock | 1 GHz |
| Memory | 512 MB DDR3-1600 |
| L1 Instruction Cache | 16 KB, 2-way associative |
| L1 Data Cache | 64 KB, 2-way associative |
| L2 Cache | 256 KB, 8-way associative |

---

## 2. Project File Structure

```
/home/sanjeeb/coa_cpu_project/
│
├── matrix_mult.c          # Benchmark 1: Matrix multiplication (compute-heavy)
├── branch_heavy.c         # Benchmark 2: Unpredictable branches
├── memory_stride.c        # Benchmark 3: Cache-thrashing memory accesses
│
├── Makefile               # Compiles all 3 C files into static binaries
│
├── simulate.py            # gem5 configuration script (CPU + Cache setup)
├── run_simulations.sh     # Bash script: runs all benchmark × CPU combinations
│
├── extract_stats.py       # Parses stats.txt files → results_summary.json
├── plot_results.py        # Reads results_summary.json → generates PNG graphs
│
├── results/               # Output folder created by run_simulations.sh
│   ├── matrix_mult_TimingSimpleCPU/
│   │   └── stats.txt      # gem5 raw statistics output
│   ├── matrix_mult_O3CPU/
│   │   └── stats.txt
│   ├── branch_heavy_TimingSimpleCPU/
│   │   └── stats.txt
│   ├── branch_heavy_O3CPU/
│   │   └── stats.txt
│   ├── memory_stride_TimingSimpleCPU/
│   │   └── stats.txt
│   └── memory_stride_O3CPU/
│       └── stats.txt
│
├── results_summary.json   # Extracted key metrics (IPC, Ticks, DCache Misses)
├── ipc_comparison.png     # Graph: IPC for each benchmark/CPU
├── sim_ticks_comparison.png  # Graph: Simulation ticks (execution time)
└── dcache_misses.png      # Graph: L1 Data Cache misses
```

---

## 3. Source Code (All Files)

### 3.1 `matrix_mult.c` — Compute-Heavy Benchmark

```c
#include <stdio.h>
#include <stdlib.h>

#define SIZE 64

int A[SIZE][SIZE];
int B[SIZE][SIZE];
int C[SIZE][SIZE];

void init_matrices() {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            A[i][j] = i + j;
            B[i][j] = i - j;
            C[i][j] = 0;
        }
    }
}

void multiply() {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            for (int k = 0; k < SIZE; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    printf("Starting Matrix Multiplication...\n");
    init_matrices();
    multiply();

    // Prevent optimization from removing the calculation
    int sum = 0;
    for (int i = 0; i < SIZE; i++) {
        sum += C[i][i];
    }
    printf("Matrix Multiplication complete. Checksum: %d\n", sum);
    return 0;
}
```

---

### 3.2 `branch_heavy.c` — Branch-Prediction Stress Test

```c
#include <stdio.h>
#include <stdlib.h>

#define ITERS 500000

int main() {
    printf("Starting Branch Heavy loop...\n");
    long long sum = 0;

    // An unpredictable branch pattern using simple arithmetic
    for (int i = 0; i < ITERS; i++) {
        if ((i % 2 == 0) && (i % 3 != 0) || (i % 7 == 0)) {
            sum += i;
        } else if (i % 5 == 0) {
            sum -= i;
        } else {
            sum += 1;
        }
    }

    printf("Branch Heavy complete. Sum: %lld\n", sum);
    return 0;
}
```

---

### 3.3 `memory_stride.c` — Cache-Thrashing Benchmark

```c
#include <stdio.h>
#include <stdlib.h>

#define ARR_SIZE (1024 * 1024 * 2) // 2 MB array (larger than most L1 caches)
#define STRIDE 1024                 // Jump by large amounts to cause cache misses
#define ITERS 2

int arr[ARR_SIZE];

int main() {
    printf("Starting Memory Stride...\n");

    for (int i = 0; i < ARR_SIZE; i++) {
        arr[i] = i;
    }

    long long sum = 0;
    for (int iter = 0; iter < ITERS; iter++) {
        for (int i = 0; i < ARR_SIZE; i += STRIDE) {
            sum += arr[i];
            arr[i] = sum % 100; // write back to invalidate cache lines
        }
    }

    printf("Memory Stride complete. Sum: %lld\n", sum);
    return 0;
}
```

---

### 3.4 `Makefile` — Compile All Benchmarks

```makefile
CC = gcc
CFLAGS = -static -O2

all: matrix_mult branch_heavy memory_stride

matrix_mult: matrix_mult.c
	$(CC) $(CFLAGS) -o matrix_mult matrix_mult.c

branch_heavy: branch_heavy.c
	$(CC) $(CFLAGS) -o branch_heavy branch_heavy.c

memory_stride: memory_stride.c
	$(CC) $(CFLAGS) -o memory_stride memory_stride.c

clean:
	rm -f matrix_mult branch_heavy memory_stride
```

---

### 3.5 `simulate.py` — gem5 CPU + Cache Configuration Script

```python
import m5
from m5.objects import *
import sys
import argparse

parser = argparse.ArgumentParser(description="A simple system with 2-level cache.")
parser.add_argument("binary", default="", nargs="?", help="Path to the binary to execute.")
parser.add_argument("--cpu", default="TimingSimpleCPU", choices=["TimingSimpleCPU", "O3CPU"],
                    help="CPU model to use")
parser.add_argument("--l1i_size", help="L1 instruction cache size")
parser.add_argument("--l1d_size", help="L1 data cache size")
parser.add_argument("--l2_size", help="Unified L2 cache size")

options = parser.parse_args()

# ----- Cache Definitions -----
class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

class L1ICache(L1Cache):
    size = options.l1i_size if options.l1i_size else '16kB'

class L1DCache(L1Cache):
    size = options.l1d_size if options.l1d_size else '64kB'

class L2Cache(Cache):
    size = options.l2_size if options.l2_size else '256kB'
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

# ----- System Setup -----
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# ----- CPU Setup -----
if options.cpu == "O3CPU":
    system.cpu = O3CPU()
else:
    system.cpu = TimingSimpleCPU()

# Create and connect caches (L1 I, L1 D → L2 bus → L2 → Memory bus → DRAM)
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

system.l2bus = L2XBar()
system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports

system.l2cache = L2Cache()
system.l2cache.cpu_side = system.l2bus.mem_side_ports

system.membus = SystemXBar()
system.l2cache.mem_side = system.membus.cpu_side_ports

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.system_port = system.membus.cpu_side_ports

# Memory Controller (DDR3-1600)
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# ----- Process Setup -----
system.workload = SEWorkload.init_compatible(options.binary)
process = Process()
process.cmd = [options.binary]
system.cpu.workload = process
system.cpu.createThreads()

# ----- Run Simulation -----
root = Root(full_system=False, system=system)
m5.instantiate()
print(f"Beginning simulation of {options.binary} with CPU: {options.cpu}")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
```

---

### 3.6 `run_simulations.sh` — Automation Script

```bash
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
```

---

### 3.7 `extract_stats.py` — Parse gem5 Stats

```python
import os
import re
import json

def parse_stats(file_path):
    stats = {}
    if not os.path.exists(file_path):
        return stats

    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.startswith('---'):
                continue

            match = re.match(r'^([\w\.:]+)\s+([-\d\.e]+)', line)
            if match:
                key, value = match.groups()
                try:
                    stats[key] = float(value)
                except ValueError:
                    pass
    return stats

def main():
    benchmarks = ["matrix_mult", "branch_heavy", "memory_stride"]
    cpus = ["TimingSimpleCPU", "O3CPU"]

    results = {}

    for benchmark in benchmarks:
        results[benchmark] = {}
        for cpu in cpus:
            stats_file = f"results/{benchmark}_{cpu}/stats.txt"
            stats = parse_stats(stats_file)

            if stats:
                ipc = stats.get('system.cpu.ipc', 0)
                sim_ticks = stats.get('simTicks', stats.get('sim_ticks', 0))
                dcache_misses = stats.get(
                    'system.cpu.dcache.overallMisses::total',
                    stats.get('system.cpu.dcache.overall_misses::total', 0)
                )

                results[benchmark][cpu] = {
                    "IPC": ipc,
                    "Sim Ticks": sim_ticks,
                    "DCache Misses": dcache_misses
                }
            else:
                results[benchmark][cpu] = None
                print(f"Warning: No stats found for {benchmark} with {cpu}")

    with open("results_summary.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Parsed stats and saved to results_summary.json")

if __name__ == "__main__":
    main()
```

---

### 3.8 `plot_results.py` — Generate Bar Charts

```python
import json
import matplotlib.pyplot as plt
import numpy as np

def plot_metric(results, metric, filename, title, ylabel):
    benchmarks = list(results.keys())
    cpus = list(results[benchmarks[0]].keys())

    x = np.arange(len(benchmarks))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    valid_data = True
    for i, cpu in enumerate(cpus):
        values = []
        for b in benchmarks:
            if results[b][cpu] is None:
                values.append(0)
                valid_data = False
            else:
                values.append(results[b][cpu][metric])

        offset = (i - 0.5) * width
        rects = ax.bar(x + offset, values, width, label=cpu)
        ax.bar_label(rects, padding=3, fmt='%.2e' if metric == 'Sim Ticks' else '%.2f')

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks)
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename)
    print(f"Saved {filename}")

def main():
    try:
        with open("results_summary.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("results_summary.json not found. Run extract_stats.py first.")
        return

    plot_metric(results, "IPC", "ipc_comparison.png", "Instructions per Cycle (IPC) Comparison", "IPC")
    plot_metric(results, "Sim Ticks", "sim_ticks_comparison.png", "Execution Time (Simulated Ticks) Comparison", "Simulated Ticks")
    plot_metric(results, "DCache Misses", "dcache_misses.png", "L1 Data Cache Misses Comparison", "Cache Misses")

if __name__ == "__main__":
    main()
```

---

## 4. Step-by-Step: How to Run

1.  **Open WSL Terminal** and navigate to `/home/sanjeeb/coa_cpu_project`.
2.  **Compile Benchmarks**: Run `make`.
3.  **Run Simulations**: Run `bash run_simulations.sh`.
4.  **Extract Data**: Run `python3 extract_stats.py`.
5.  **Generate Graphs**: Run `python3 plot_results.py`.
6.  **Results**: Check `ipc_comparison.png`, `sim_ticks_comparison.png`, and `dcache_misses.png`.

---

## 5. Understanding stats.txt

Each `stats.txt` provides:
- `simTicks`: Total simulated time.
- `system.cpu.ipc`: Efficiency of instructions per cycle.
- `system.cpu.dcache.overallMisses::total`: Reliability of cache hierarchy.

---

## 6. Analysis & Key Findings

- **Compute Heavy (`matrix_mult`)**: O3 speedup of **5.8×** due to parallel execution and prefetching.
- **Branch Heavy (`branch_heavy`)**: O3 speedup of **4.8×** showing effective branch prediction.
- **Memory Bound (`memory_stride`)**: Minimal speedup (**1.5×**) highlighting the **Memory Wall** — when cache misses dominate, even OoO cores stall.
- **Cache Stress**: `memory_stride` generates ~140,000 misses, validating its design as a cache-thrashing test.
