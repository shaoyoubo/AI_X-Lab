#!/bin/bash
# Lab4 Baseline Experiment Script - 3D Torus with Deterministic Routing (routing=3)
# 3D Torus 4x4x4, 64 CPUs, 64 dirs, deterministic DOR routing

# Set results directory
results_dir="./results/baseline"
mkdir -p $results_dir

echo "Starting Lab4 Baseline Experiment: 3D Torus with Deterministic Routing"
echo "Configuration: 4x4x4 3D Torus, 64 CPUs, 64 dirs, deterministic routing (algorithm=3)"
echo "=============================================================================="

# 8 types of traffic patterns
traffic_patterns=("uniform_random" "shuffle" "transpose" "tornado" "neighbor" "bit_complement" "bit_reverse" "bit_rotation")

# injection rates from 0.01 to 1.0
# injection_rates=(0.01 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)
injection_rates=(0.1 0.2 0.3 0.4 0.5 0.6 0.8)

for pattern in "${traffic_patterns[@]}"; do
    echo ""
    echo "Testing traffic pattern: $pattern"
    echo "----------------------------------------"

    # Create result file for this pattern
    result_file="$results_dir/${pattern}_baseline_results.csv"
    > $result_file  # Clear file

    for rate in "${injection_rates[@]}"; do
        echo "  Injection Rate: $rate"

        # Change to gem5 directory (go back to main directory)
        cd /home/wly-wsl/AI_X-Lab

        # Run gem5 simulation with deterministic routing (routing=3)
        ./build/NULL/gem5.opt configs/example/garnet_synth_traffic.py \
            --network=garnet --num-cpus=64 --num-dirs=64 \
            --topology=Torus3D --torus-x=4 --torus-y=4 --torus-z=4 \
            --routing-algorithm=3 --synthetic=$pattern \
            --sim-cycles=10000 --injectionrate=$rate \
            --inj-vnet=2 \
            --vcs-per-vnet=4 \
            > /dev/null 2>&1

        # Check if simulation succeeded
        if [ $? -eq 0 ]; then
            # Extract statistics
            packets_received=$(grep "packets_received::total" m5out/stats.txt | awk '{print $2}')
            packets_injected=$(grep "packets_injected::total" m5out/stats.txt | awk '{print $2}')
            avg_packet_latency=$(grep "average_packet_latency" m5out/stats.txt | awk '{print $2}')
            avg_hops=$(grep "average_hops" m5out/stats.txt | awk '{print $2}')

            # Extract network latency and queuing latency
            avg_packet_network_latency=$(grep "average_packet_network_latency" m5out/stats.txt | awk '{print $2}')
            avg_packet_queueing_latency=$(grep "average_packet_queueing_latency" m5out/stats.txt | awk '{print $2}')

            # If specific network and queueing latency not found, try other possible names
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
                echo "    Warning: No packets received for rate $rate"
                throughput="0.000000"
                per_node_throughput="0.000000"
            fi

            # Save results to CSV file
            echo "$rate,$throughput,$per_node_throughput,$avg_packet_latency,$avg_hops,$avg_packet_network_latency,$avg_packet_queueing_latency,$packets_received,$packets_injected" >> $result_file

            echo "    Throughput: $throughput packets/cycle"
            echo "    Per-node Throughput: $per_node_throughput packets/node/cycle"
            echo "    Average Latency: $avg_packet_latency cycles"
            echo "    Average Hops: $avg_hops"
            echo "    Network Latency: $avg_packet_network_latency cycles"
            echo "    Queueing Latency: $avg_packet_queueing_latency cycles"
        else
            echo "    Error: Simulation failed for rate $rate"
            # Record failure case
            echo "$rate,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED" >> $result_file
        fi

        echo ""
    done

    # Add CSV header
    sed -i '1i injection_rate,throughput,per_node_throughput,avg_latency,avg_hops,network_latency,queueing_latency,packets_received,packets_injected' $result_file

    echo "Baseline results for $pattern saved to $result_file"
    echo "========================================"
done

echo ""
echo "All baseline experiments completed!"
echo "Results saved in: $results_dir"
echo "Including the following files:"
ls -la $results_dir/*.csv
echo ""
echo "Use Python scripts to compare with adaptive routing results."
