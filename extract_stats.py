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
            
            # Match lines like "system.cpu.ipc 1.45 # IPC" or "system.cpu.dcache.overallMisses::total 123"
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
                dcache_misses = stats.get('system.cpu.dcache.overallMisses::total', stats.get('system.cpu.dcache.overall_misses::total', 0))
                
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
