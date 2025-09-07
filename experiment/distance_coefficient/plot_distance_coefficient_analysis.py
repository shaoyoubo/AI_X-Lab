#!/usr/bin/env python3
"""
Distance Coefficient Analysis Script for Lab4 experiment
Compares different distance coefficient values in adaptive routing
Generates a 2x2 subplot figure with 5 curves per plot
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


def load_data(results_dir, pattern, distance_coefficients):
    """
    Load data for all distance coefficient values
    """
    data_dict = {}

    for dist_coeff in distance_coefficients:
        filename = f"{pattern}_distcoeff{dist_coeff}_results.csv"
        filepath = os.path.join(results_dir, filename)

        try:
            df = pd.read_csv(filepath)
            # Filter out failed runs
            df = df[df["throughput"] != "FAILED"]
            df = df.apply(pd.to_numeric, errors="coerce")
            df = df.dropna()

            if len(df) > 0:
                data_dict[dist_coeff] = df
                print(
                    f"✓ Loaded data for distance coefficient {dist_coeff}: {len(df)} data points"
                )
            else:
                print(f"✗ No valid data for distance coefficient {dist_coeff}")

        except FileNotFoundError:
            print(f"✗ File not found: {filepath}")
        except Exception as e:
            print(f"✗ Error loading {filepath}: {e}")

    return data_dict


def create_analysis_plot(data_dict, pattern, output_dir):
    """
    Create a 2x2 analysis plot for distance coefficient comparison
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        f'Distance Coefficient Analysis: {pattern.replace("_", " ").title()}\n'
        f"Impact of Distance Preference in Adaptive Routing",
        fontsize=14,
        fontweight="bold",
    )

    # Color scheme for different distance coefficients
    colors = {
        -4: "#d62728",  # Red (conservative)
        -2: "#ff7f0e",  # Orange
        0: "#2ca02c",  # Green (pure congestion)
        2: "#1f77b4",  # Blue
        4: "#9467bd",  # Purple (load balancing)
    }

    # Line styles for better distinction
    linestyles = {
        -4: "-",  # Solid
        -2: "--",  # Dashed
        0: "-.",  # Dash-dot
        2: ":",  # Dotted
        4: "-",  # Solid
    }

    # Plot 1: Latency vs Throughput
    ax1 = axes[0, 0]
    for dist_coeff, df in data_dict.items():
        label = f"DC={dist_coeff}"
        if dist_coeff < 0:
            label += " (Conservative)"
        elif dist_coeff == 0:
            label += " (Pure Congestion)"
        else:
            label += " (Load Balancing)"

        ax1.plot(
            df["throughput"],
            df["avg_latency"],
            color=colors[dist_coeff],
            linestyle=linestyles[dist_coeff],
            label=label,
            linewidth=2,
            markersize=3,
            marker="o",
        )

    ax1.set_xlabel("Throughput (packets/cycle)")
    ax1.set_ylabel("Average Latency (ticks)")
    ax1.set_title("Latency vs Throughput")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Latency vs Throughput (Log Scale)
    ax2 = axes[0, 1]
    for dist_coeff, df in data_dict.items():
        label = f"DC={dist_coeff}"
        ax2.plot(
            df["throughput"],
            df["avg_latency"],
            color=colors[dist_coeff],
            linestyle=linestyles[dist_coeff],
            label=label,
            linewidth=2,
            markersize=3,
            marker="s",
        )

    ax2.set_xlabel("Throughput (packets/cycle)")
    ax2.set_ylabel("Average Latency (ticks)")
    ax2.set_yscale("log")
    ax2.set_title("Latency vs Throughput (Log Scale)")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Plot 3: Average Hops vs Throughput
    ax3 = axes[1, 0]
    for dist_coeff, df in data_dict.items():
        label = f"DC={dist_coeff}"
        ax3.plot(
            df["throughput"],
            df["avg_hops"],
            color=colors[dist_coeff],
            linestyle=linestyles[dist_coeff],
            label=label,
            linewidth=2,
            markersize=3,
            marker="^",
        )

    ax3.set_xlabel("Throughput (packets/cycle)")
    ax3.set_ylabel("Average Hops")
    ax3.set_title("Average Hops vs Throughput")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Plot 4: Throughput vs Injection Rate
    ax4 = axes[1, 1]
    for dist_coeff, df in data_dict.items():
        label = f"DC={dist_coeff}"
        ax4.plot(
            df["injection_rate"],
            df["throughput"],
            color=colors[dist_coeff],
            linestyle=linestyles[dist_coeff],
            label=label,
            linewidth=2,
            markersize=3,
            marker="d",
        )

    ax4.set_xlabel("Injection Rate")
    ax4.set_ylabel("Throughput (packets/cycle)")
    ax4.set_title("Throughput vs Injection Rate")
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    # Adjust layout and save
    plt.tight_layout()
    output_file = os.path.join(
        output_dir, f"{pattern}_distance_coefficient_analysis.pdf"
    )
    plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

    return output_file


def generate_summary_stats(data_dict, pattern):
    """
    Generate summary statistics for distance coefficient comparison
    """
    stats = []

    for dist_coeff, df in data_dict.items():
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

        stats.append(
            {
                "distance_coefficient": dist_coeff,
                "max_throughput": max_throughput,
                "min_latency": min_latency,
                "latency_at_50pct_throughput": latency_at_50pct,
                "avg_hops_mean": avg_hops_mean,
                "routing_type": "Conservative"
                if dist_coeff < 0
                else "Pure Congestion"
                if dist_coeff == 0
                else "Load Balancing",
            }
        )

    return stats


def main():
    """
    Main function to generate distance coefficient analysis plots
    """
    # Define directories
    base_dir = "./"
    results_dir = os.path.join(base_dir, "results", "distance_coefficient")
    output_dir = os.path.join(base_dir, "results", "distance_coefficient")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Traffic pattern (only bit_reverse)
    pattern = "bit_reverse"

    # Distance coefficient values
    distance_coefficients = [-4, -2, 0, 2, 4]

    # Check if results directory exists
    if not os.path.exists(results_dir):
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run the distance coefficient experiments first.")
        return

    print("Generating distance coefficient analysis plots...")
    print("=" * 50)
    print(f"Pattern: {pattern}")
    print(f"Distance coefficients: {distance_coefficients}")
    print("")

    # Load data
    data_dict = load_data(results_dir, pattern, distance_coefficients)

    if not data_dict:
        print("Error: No data loaded successfully!")
        return

    print(
        f"\nSuccessfully loaded data for {len(data_dict)} distance coefficients"
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
                output_dir, f"{pattern}_distance_coefficient_summary.csv"
            )
            stats_df.to_csv(stats_file, index=False)
            print(f"✓ Summary statistics saved to: {stats_file}")

            # Print summary
            print("\n" + "=" * 50)
            print("DISTANCE COEFFICIENT ANALYSIS SUMMARY")
            print("=" * 50)
            for stat in stats:
                print(
                    f"\nDistance Coefficient {stat['distance_coefficient']} ({stat['routing_type']}):"
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
    print("Distance coefficient analysis completed!")
    print(f"Output directory: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
