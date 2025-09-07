#!/bin/bash
# Lab4 Injection Virtual Network Experiment Script
# Study the impact of different injection virtual networks in adaptive routing
# 3D Torus 4x4x4, 64 CPUs, 64 dirs, adaptive routing (algorithm=4)

# Set results directory
results_dir="./results/inj_vnet"
mkdir -p $results_dir

echo "Starting Lab4 Experiment: Impact of injection virtual network settings"
echo "Configuration: 4x4x4 3D Torus, 64 CPUs, 64 dirs, adaptive routing (algorithm=4)"
echo "Testing inj-vnet values: -1 (random), 0 (control), 1 (control), 2 (data)"
echo "Traffic pattern: bit_reverse"
echo "========================================================================"

# Using only bit_reverse traffic pattern
pattern="bit_reverse"

# Injection virtual network values to test
# -1: randomly inject in all vnets
# 0: vnet 0 (control packets, 1-flit)
# 1: vnet 1 (control packets, 1-flit)
# 2: vnet 2 (data packets, 5-flit)
inj_vnet_values=(-1 0 2)

# injection rates from 0.01 to 1.0
injection_rates=(0.01 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)

# Function to extract statistics
extract_stats() {
    local rate=$1

    # Extract statistics
    packets_received=$(grep "packets_received::total" m5out/stats.txt | awk '{print $2}')
    packets_injected=$(grep "packets_injected::total" m5out/stats.txt | awk '{print $2}')
    avg_packet_latency=$(grep "average_packet_latency" m5out/stats.txt | awk '{print $2}')
    avg_hops=$(grep "average_hops" m5out/stats.txt | awk '{print $2}')

    # Extract network latency and queuing latency
    avg_packet_network_latency=$(grep "average_packet_network_latency" m5out/stats.txt | awk '{print $2}')
    avg_packet_queueing_latency=$(grep "average_packet_queueing_latency" m5out/stats.txt | awk '{print $2}')

    # Try alternative names if not found
    if [ -z "$avg_packet_network_latency" ] || [ "$avg_packet_network_latency" = "(Unspecified)" ]; then
        avg_packet_network_latency=$(grep "avg_packet_network_latency" m5out/stats.txt | awk '{print $2}')
    fi
    if [ -z "$avg_packet_queueing_latency" ] || [ "$avg_packet_queueing_latency" = "(Unspecified)" ]; then
        avg_packet_queueing_latency=$(grep "avg_packet_queueing_latency" m5out/stats.txt | awk '{print $2}')
    fi

    # Handle (Unspecified) values
    [ "$packets_received" = "(Unspecified)" ] && packets_received="0"
    [ "$packets_injected" = "(Unspecified)" ] && packets_injected="0"
    [ "$avg_packet_latency" = "(Unspecified)" ] && avg_packet_latency="0"
    [ "$avg_hops" = "(Unspecified)" ] && avg_hops="0"
    [ "$avg_packet_network_latency" = "(Unspecified)" ] && avg_packet_network_latency="0"
    [ "$avg_packet_queueing_latency" = "(Unspecified)" ] && avg_packet_queueing_latency="0"

    # Calculate throughput
    if [ ! -z "$packets_received" ] && [ "$packets_received" != "0" ]; then
        throughput=$(python3 -c "print(f'{$packets_received / 10000:.6f}')")
        per_node_throughput=$(python3 -c "print(f'{($packets_received / 10000) / 64:.6f}')")
    else
        throughput="0.000000"
        per_node_throughput="0.000000"
    fi

    echo "$rate,$throughput,$per_node_throughput,$avg_packet_latency,$avg_hops,$avg_packet_network_latency,$avg_packet_queueing_latency,$packets_received,$packets_injected"
}

# Main experiment loop - only bit_reverse pattern
echo ""
echo "Testing traffic pattern: $pattern"
echo "=================================================="

for inj_vnet in "${inj_vnet_values[@]}"; do
    echo ""
    if [ $inj_vnet -eq -1 ]; then
        echo "Injection VNet: $inj_vnet (random injection in all vnets)"
    elif [ $inj_vnet -eq 0 ] || [ $inj_vnet -eq 1 ]; then
        echo "Injection VNet: $inj_vnet (control packets, 1-flit)"
    else
        echo "Injection VNet: $inj_vnet (data packets, 5-flit)"
    fi
    echo "-----------------------------------"

    # Create result file for this combination
    result_file="$results_dir/${pattern}_injvnet${inj_vnet}_results.csv"
    > $result_file  # Clear file

    # Add CSV header
    echo "injection_rate,throughput,per_node_throughput,avg_latency,avg_hops,network_latency,queueing_latency,packets_received,packets_injected" > $result_file

    for rate in "${injection_rates[@]}"; do
        echo "  Injection Rate: $rate"

        # Run gem5 simulation
        ./build/NULL/gem5.opt configs/example/garnet_synth_traffic.py \
            --network=garnet --num-cpus=64 --num-dirs=64 \
            --topology=Torus3D --torus-x=4 --torus-y=4 --torus-z=4 \
            --routing-algorithm=4 --synthetic=$pattern \
            --sim-cycles=10000 --injectionrate=$rate \
            --inj-vnet=$inj_vnet --adaptive-tie-breaking=x_first \
            --vcs-per-vnet=4 \
            --escape-vcs=1 \
            > /dev/null 2>&1

        # Check if simulation succeeded
        if [ $? -eq 0 ]; then
            # Extract and save statistics
            stats_line=$(extract_stats "$rate")
            echo "$stats_line" >> $result_file

            # Display progress
            throughput=$(echo "$stats_line" | cut -d',' -f2)
            latency=$(echo "$stats_line" | cut -d',' -f4)
            echo "    Throughput: $throughput, Latency: $latency"
        else
            echo "    FAILED: Rate $rate"
            echo "$rate,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED" >> $result_file
        fi
    done

    echo "Results saved to: $result_file"
done

echo ""
echo "========================================"
echo "All injection vnet experiments completed!"
echo "Results directory: $results_dir"
echo ""
echo "Generated files:"
ls -la $results_dir/*.csv
echo ""
echo "Files generated:"
for inj_vnet in "${inj_vnet_values[@]}"; do
    echo "  ${pattern}_injvnet${inj_vnet}_results.csv"
done
echo ""
echo "Virtual Network Information:"
echo "  VNet -1: Random injection across all virtual networks"
echo "  VNet 0:  Control packets (ReadReq, 1-flit)"
echo "  VNet 1:  Control packets (INST_FETCH, 1-flit)"
echo "  VNet 2:  Data packets (WriteReq, 5-flit)"
echo ""
echo "Use plot_inj_vnet.py to generate injection vnet comparison plots."
