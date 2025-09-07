#!/usr/bin/env python3
"""
Injection Virtual Network Analysis Script for Lab4 experiment
Compares different injection virtual network settings in adaptive routing
Generates a 2x2 subplot figure with 4 curves per plot
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pathlib import Path

# Set up matplotlib for better plots
plt.rcParams["figure.figsize"] = (12, 10)
plt.rcParams["font.size"] = 10
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def load_data(results_dir, pattern, inj_vnet_values):
    """
    Load data for all injection virtual network values
    """
    data_dict = {}

    for inj_vnet in inj_vnet_values:
        filename = f"{pattern}_injvnet{inj_vnet}_results.csv"
        filepath = os.path.join(results_dir, filename)

        try:
            df = pd.read_csv(filepath)
            # Filter out failed runs
            df = df[df["throughput"] != "FAILED"]
            df = df.apply(pd.to_numeric, errors="coerce")
            df = df.dropna()

            if len(df) > 0:
                data_dict[inj_vnet] = df
                print(
                    f"✓ Loaded data for inj-vnet {inj_vnet}: {len(df)} data points"
                )
            else:
                print(f"✗ No valid data for inj-vnet {inj_vnet}")

        except FileNotFoundError:
            print(f"✗ File not found: {filepath}")
        except Exception as e:
            print(f"✗ Error loading {filepath}: {e}")

    return data_dict


def create_analysis_plot(data_dict, pattern, output_dir):
    """
    Create a 2x2 analysis plot for injection vnet comparison
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        f'Injection Virtual Network Analysis: {pattern.replace("_", " ").title()}\n'
        f"Impact of Different VNet Injection Strategies",
        fontsize=14,
        fontweight="bold",
    )

    # Color scheme for different injection vnets
    colors = {
        -1: "#2ca02c",  # Green (random)
        0: "#1f77b4",  # Blue (control vnet 0)
        1: "#ff7f0e",  # Orange (control vnet 1)
        2: "#d62728",  # Red (data vnet 2)
    }

    # Line styles and markers for better distinction
    linestyles = {
        -1: "-",  # Solid
        0: "--",  # Dashed
        1: "-.",  # Dash-dot
        2: ":",  # Dotted
    }

    markers = {
        -1: "o",  # Circle
        0: "s",  # Square
        1: "^",  # Triangle up
        2: "d",  # Diamond
    }

    # Plot 1: Latency vs Throughput
    ax1 = axes[0, 0]
    for inj_vnet, df in data_dict.items():
        if inj_vnet == -1:
            label = "VNet -1 (Random)"
        elif inj_vnet in [0, 1]:
            label = f"VNet {inj_vnet} (Control, 1-flit)"
        else:
            label = f"VNet {inj_vnet} (Data, 5-flit)"

        ax1.plot(
            df["throughput"],
            df["avg_latency"],
            color=colors[inj_vnet],
            linestyle=linestyles[inj_vnet],
            marker=markers[inj_vnet],
            label=label,
            linewidth=2,
            markersize=4,
        )

    ax1.set_xlabel("Throughput (packets/cycle)")
    ax1.set_ylabel("Average Latency (ticks)")
    ax1.set_title("Latency vs Throughput")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Latency vs Throughput (Log Scale)
    ax2 = axes[0, 1]
    for inj_vnet, df in data_dict.items():
        if inj_vnet == -1:
            label = "VNet -1"
        else:
            label = f"VNet {inj_vnet}"

        ax2.plot(
            df["throughput"],
            df["avg_latency"],
            color=colors[inj_vnet],
            linestyle=linestyles[inj_vnet],
            marker=markers[inj_vnet],
            label=label,
            linewidth=2,
            markersize=4,
        )

    ax2.set_xlabel("Throughput (packets/cycle)")
    ax2.set_ylabel("Average Latency (ticks)")
    ax2.set_yscale("log")
    ax2.set_title("Latency vs Throughput (Log Scale)")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Plot 3: Average Hops vs Throughput
    ax3 = axes[1, 0]
    for inj_vnet, df in data_dict.items():
        if inj_vnet == -1:
            label = "VNet -1"
        else:
            label = f"VNet {inj_vnet}"

        ax3.plot(
            df["throughput"],
            df["avg_hops"],
            color=colors[inj_vnet],
            linestyle=linestyles[inj_vnet],
            marker=markers[inj_vnet],
            label=label,
            linewidth=2,
            markersize=4,
        )

    ax3.set_xlabel("Throughput (packets/cycle)")
    ax3.set_ylabel("Average Hops")
    ax3.set_title("Average Hops vs Throughput")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    # Plot 4: Throughput vs Injection Rate
    ax4 = axes[1, 1]
    for inj_vnet, df in data_dict.items():
        if inj_vnet == -1:
            label = "VNet -1"
        else:
            label = f"VNet {inj_vnet}"

        ax4.plot(
            df["injection_rate"],
            df["throughput"],
            color=colors[inj_vnet],
            linestyle=linestyles[inj_vnet],
            marker=markers[inj_vnet],
            label=label,
            linewidth=2,
            markersize=4,
        )

    ax4.set_xlabel("Injection Rate")
    ax4.set_ylabel("Throughput (packets/cycle)")
    ax4.set_title("Throughput vs Injection Rate")
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)

    # Adjust layout and save
    plt.tight_layout()
    output_file = os.path.join(output_dir, f"{pattern}_inj_vnet_analysis.pdf")
    plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

    return output_file


def generate_summary_stats(data_dict, pattern):
    """
    Generate summary statistics for injection vnet comparison
    """
    stats = []

    for inj_vnet, df in data_dict.items():
        if len(df) == 0:
            continue

        max_throughput = df["throughput"].max()
        min_latency = df["avg_latency"].min()

        # Find latency at 50% of max throughput
        target_throughput = max_throughput * 0.5
        latency_at_50pct = np.interp(
            target_throughput, df["throughput"], df["avg_latency"]
        )

        # Average hops
        avg_hops_mean = df["avg_hops"].mean()

        # VNet type description
        if inj_vnet == -1:
            vnet_type = "Random injection"
            packet_type = "Mixed (1-flit & 5-flit)"
        elif inj_vnet in [0, 1]:
            vnet_type = "Control packets"
            packet_type = "1-flit"
        else:
            vnet_type = "Data packets"
            packet_type = "5-flit"

        stats.append(
            {
                "inj_vnet": inj_vnet,
                "vnet_type": vnet_type,
                "packet_type": packet_type,
                "max_throughput": max_throughput,
                "min_latency": min_latency,
                "latency_at_50pct_throughput": latency_at_50pct,
                "avg_hops_mean": avg_hops_mean,
            }
        )

    return stats


def main():
    """
    Main function to generate injection vnet analysis plots
    """
    # Define directories
    base_dir = "./"
    results_dir = os.path.join(base_dir, "results", "inj_vnet")
    output_dir = os.path.join(base_dir, "results", "inj_vnet")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Traffic pattern (only bit_reverse)
    pattern = "bit_reverse"

    # Injection vnet values
    inj_vnet_values = [-1, 0, 1, 2]

    # Check if results directory exists
    if not os.path.exists(results_dir):
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run the injection vnet experiments first.")
        return

    print("Generating injection virtual network analysis plots...")
    print("=" * 50)
    print(f"Pattern: {pattern}")
    print(f"Injection VNet values: {inj_vnet_values}")
    print("")

    # Load data
    data_dict = load_data(results_dir, pattern, inj_vnet_values)

    if not data_dict:
        print("Error: No data loaded successfully!")
        return

    print(
        f"\nSuccessfully loaded data for {len(data_dict)} injection vnet configurations"
    )

    # Generate analysis plot
    try:
        output_file = create_analysis_plot(data_dict, pattern, output_dir)
        print(f"✓ Created analysis plot: {output_file}")

        # Generate summary statistics
        stats = generate_summary_stats(data_dict, pattern)
        if stats:
            stats_df = pd.DataFrame(stats)
            stats_file = os.path.join(
                output_dir, f"{pattern}_inj_vnet_summary.csv"
            )
            stats_df.to_csv(stats_file, index=False)
            print(f"✓ Summary statistics saved to: {stats_file}")

            # Print summary
            print("\n" + "=" * 50)
            print("INJECTION VIRTUAL NETWORK ANALYSIS SUMMARY")
            print("=" * 50)
            for stat in stats:
                print(
                    f"\nInj-VNet {stat['inj_vnet']} ({stat['vnet_type']}, {stat['packet_type']}):"
                )
                print(
                    f"  Max Throughput: {stat['max_throughput']:.6f} packets/cycle"
                )
                print(f"  Min Latency: {stat['min_latency']:.2f} ticks")
                print(
                    f"  Latency at 50% throughput: {stat['latency_at_50pct_throughput']:.2f} ticks"
                )
                print(f"  Average hops: {stat['avg_hops_mean']:.2f}")

    except Exception as e:
        print(f"✗ Error creating analysis plot: {e}")
        return

    print(f"\n" + "=" * 50)
    print("Injection virtual network analysis completed!")
    print(f"Output directory: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
