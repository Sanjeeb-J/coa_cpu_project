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
