#!/usr/bin/env python3
"""
Lab4 Results Plotting Script
Generates 4 plots in a 2x2 layout showing the performance of different synthetic traffic patterns
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import glob


def load_results(results_dir):
    """Load all CSV result files from the results directory"""
    csv_files = glob.glob(os.path.join(results_dir, "*_results.csv"))

    if not csv_files:
        print(f"No CSV files found in {results_dir}")
        return {}

    data = {}
    for file in csv_files:
        pattern_name = os.path.basename(file).replace("_results.csv", "")
        try:
            df = pd.read_csv(file)
            # Filter out failed simulations
            df = df[df["throughput"] != "FAILED"]
            # Convert columns to numeric
            numeric_cols = [
                "injection_rate",
                "throughput",
                "per_node_throughput",
                "avg_latency",
                "avg_hops",
                "network_latency",
                "queueing_latency",
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Remove rows with NaN values
            df = df.dropna()

            if not df.empty:
                data[pattern_name] = df
                print(f"Loaded {len(df)} data points for {pattern_name}")
            else:
                print(f"Warning: No valid data for {pattern_name}")
        except Exception as e:
            print(f"Error loading {file}: {e}")

    return data


def create_plots(data, output_file):
    """Create 4 plots in a 2x2 layout and save to PDF"""

    # Set up the figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "3D Torus Network Performance Analysis\n(4x4x4, 64 CPUs, Adaptive Routing)",
        fontsize=16,
        fontweight="bold",
    )

    # Define colors for different traffic patterns
    colors = plt.cm.tab10(np.linspace(0, 1, len(data)))

    # Plot 1: Latency vs Throughput
    ax1 = axes[0, 0]
    for i, (pattern, df) in enumerate(data.items()):
        ax1.plot(
            df["throughput"],
            df["avg_latency"],
            "o-",
            label=pattern.replace("_", " ").title(),
            color=colors[i],
            markersize=4,
            linewidth=2,
        )

    ax1.set_xlabel("Throughput (packets/cycle)")
    ax1.set_ylabel("Average Latency (ticks)")
    ax1.set_title("Average Latency vs Throughput")
    ax1.grid(True, alpha=0.3)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

    # Plot 2: Latency vs Throughput (Log Scale)
    ax2 = axes[0, 1]
    for i, (pattern, df) in enumerate(data.items()):
        ax2.semilogy(
            df["throughput"],
            df["avg_latency"],
            "o-",
            label=pattern.replace("_", " ").title(),
            color=colors[i],
            markersize=4,
            linewidth=2,
        )

    ax2.set_xlabel("Throughput (packets/cycle)")
    ax2.set_ylabel("Average Latency (ticks) - Log Scale")
    ax2.set_title("Average Latency vs Throughput (Log Scale)")
    ax2.grid(True, alpha=0.3)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

    # Plot 3: Average Hops vs Throughput
    ax3 = axes[1, 0]
    for i, (pattern, df) in enumerate(data.items()):
        ax3.plot(
            df["throughput"],
            df["avg_hops"],
            "o-",
            label=pattern.replace("_", " ").title(),
            color=colors[i],
            markersize=4,
            linewidth=2,
        )

    ax3.set_xlabel("Throughput (packets/cycle)")
    ax3.set_ylabel("Average Hops")
    ax3.set_title("Average Hops vs Throughput")
    ax3.grid(True, alpha=0.3)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

    # Plot 4: Throughput vs Injection Rate
    ax4 = axes[1, 1]
    for i, (pattern, df) in enumerate(data.items()):
        ax4.plot(
            df["injection_rate"],
            df["throughput"],
            "o-",
            label=pattern.replace("_", " ").title(),
            color=colors[i],
            markersize=4,
            linewidth=2,
        )

    ax4.set_xlabel("Injection Rate (packets/node/cycle)")
    ax4.set_ylabel("Throughput (packets/cycle)")
    ax4.set_title("Throughput vs Injection Rate")
    ax4.grid(True, alpha=0.3)
    ax4.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, right=0.85)

    # Save to PDF
    with PdfPages(output_file) as pdf:
        pdf.savefig(fig, bbox_inches="tight", dpi=300)
        print(f"Plots saved to {output_file}")

    plt.close()


def print_summary_statistics(data):
    """Print summary statistics for all traffic patterns"""
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    for pattern, df in data.items():
        print(f"\n{pattern.replace('_', ' ').title()}:")
        print(f"  Max Throughput: {df['throughput'].max():.6f} packets/cycle")
        print(f"  Min Latency: {df['avg_latency'].min():.2f} cycles")
        print(f"  Max Injection Rate: {df['injection_rate'].max():.3f}")

        # Find saturation point (where latency starts increasing rapidly)
        if len(df) > 1:
            latency_increase = df["avg_latency"].diff()
            if latency_increase.max() > 0:
                saturation_idx = latency_increase.idxmax()
                saturation_throughput = df.loc[saturation_idx, "throughput"]
                print(
                    f"  Saturation Throughput: ~{saturation_throughput:.6f} packets/cycle"
                )


def main():
    """Main function"""
    results_dir = "./results/synthetic"
    output_file = "./results/synthetic/performance_analysis.pdf"

    # Check if results directory exists
    if not os.path.exists(results_dir):
        print(f"Results directory {results_dir} does not exist!")
        print(
            "Please run the experiments first using run_synthetic_experiments.sh"
        )
        return

    # Load data
    print("Loading experimental results...")
    data = load_results(results_dir)

    if not data:
        print("No valid data found. Please check your experiment results.")
        return

    print(f"Found data for {len(data)} traffic patterns:")
    for pattern in data.keys():
        print(f"  - {pattern}")

    # Create plots
    print("\nGenerating plots...")
    create_plots(data, output_file)

    # Print summary statistics
    print_summary_statistics(data)

    print(f"\nAnalysis complete! Check {output_file} for the plots.")


if __name__ == "__main__":
    main()
