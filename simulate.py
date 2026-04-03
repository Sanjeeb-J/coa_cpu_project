import m5
from m5.objects import *
import sys
import argparse

parser = argparse.ArgumentParser(description="A simple system with 2-level cache.")
parser.add_argument("binary", default="", nargs="?", help="Path to the binary to execute.")
parser.add_argument("--cpu", default="TimingSimpleCPU", choices=["TimingSimpleCPU", "O3CPU"], help="CPU model to use (TimingSimpleCPU or O3CPU)")
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

# Set the clock frequency of the system
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

# Create caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Connect L1 caches to CPU
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Create an L2 bus and connect L1 caches
system.l2bus = L2XBar()
system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports

# Create L2 cache and connect
system.l2cache = L2Cache()
system.l2cache.cpu_side = system.l2bus.mem_side_ports

# Connect L2 to memory bus
system.membus = SystemXBar()
system.l2cache.mem_side = system.membus.cpu_side_ports

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports

# Connect system port
system.system_port = system.membus.cpu_side_ports

# Memory controller
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
