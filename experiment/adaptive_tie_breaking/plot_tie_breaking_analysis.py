#!/usr/bin/env python3
"""
Adaptive Tie-Breaking Analysis Script for Lab4 experiment
Compares different tie-breaking strategies (x_first, uniform, z_first) in adaptive routing
Generates a single PDF with 2x2 subplots showing performance comparison
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


def load_tie_breaking_data(results_dir, pattern):
    """
    Load data for all tie-breaking strategies for bit_reverse pattern
    """
    tie_strategies = ["x_first", "uniform", "z_first"]
    data = {}

    for strategy in tie_strategies:
        file_path = os.path.join(
            results_dir, f"{pattern}_{strategy}_results.csv"
        )
        try:
            df = pd.read_csv(file_path)
            # Filter out failed runs
            df = df[df["throughput"] != "FAILED"]
            df = df.apply(pd.to_numeric, errors="coerce")
            df = df.dropna()
            data[strategy] = df
            print(f"✓ Loaded {len(df)} data points for {strategy}")
        except FileNotFoundError:
            print(f"✗ Error: Could not find {file_path}")
            return None
        except Exception as e:
            print(f"✗ Error loading {strategy} data: {e}")
            return None

    return data


def create_tie_breaking_comparison_plot(data_dict, pattern, output_dir):
    """
    Create a 2x2 comparison plot for tie-breaking strategies
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        f'Adaptive Tie-Breaking Strategy Comparison: {pattern.replace("_", " ").title()}\n'
        f"3D Torus 4x4x4, Adaptive Routing Algorithm",
        fontsize=14,
        fontweight="bold",
    )

    # Colors for the three strategies
    colors = {
        "x_first": "#1f77b4",  # Blue
        "uniform": "#ff7f0e",  # Orange
        "z_first": "#2ca02c",  # Green
    }

    # Markers for the three strategies
    markers = {
        "x_first": "o",  # Circle
        "uniform": "s",  # Square
        "z_first": "^",  # Triangle
    }

    # Labels for legend
    labels = {
        "x_first": "X-First (Default)",
        "uniform": "Uniform (Random)",
        "z_first": "Z-First",
    }

    # Plot 1: Latency vs Throughput
    ax1 = axes[0, 0]
    for strategy in ["x_first", "uniform", "z_first"]:
        if strategy in data_dict:
            df = data_dict[strategy]
            ax1.plot(
                df["throughput"],
                df["avg_latency"],
                marker=markers[strategy],
                color=colors[strategy],
                label=labels[strategy],
                linewidth=2,
                markersize=4,
            )
    ax1.set_xlabel("Throughput (packets/cycle)")
    ax1.set_ylabel("Average Latency (ticks)")
    ax1.set_title("Latency vs Throughput")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Latency vs Throughput (Log Scale)
    ax2 = axes[0, 1]
    for strategy in ["x_first", "uniform", "z_first"]:
        if strategy in data_dict:
            df = data_dict[strategy]
            ax2.plot(
                df["throughput"],
                df["avg_latency"],
                marker=markers[strategy],
                color=colors[strategy],
                label=labels[strategy],
                linewidth=2,
                markersize=4,
            )
    ax2.set_xlabel("Throughput (packets/cycle)")
    ax2.set_ylabel("Average Latency (ticks)")
    ax2.set_yscale("log")
    ax2.set_title("Latency vs Throughput (Log Scale)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Average Hops vs Throughput
    ax3 = axes[1, 0]
    for strategy in ["x_first", "uniform", "z_first"]:
        if strategy in data_dict:
            df = data_dict[strategy]
            ax3.plot(
                df["throughput"],
                df["avg_hops"],
                marker=markers[strategy],
                color=colors[strategy],
                label=labels[strategy],
                linewidth=2,
                markersize=4,
            )
    ax3.set_xlabel("Throughput (packets/cycle)")
    ax3.set_ylabel("Average Hops")
    ax3.set_title("Average Hops vs Throughput")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Plot 4: Throughput vs Injection Rate
    ax4 = axes[1, 1]
    for strategy in ["x_first", "uniform", "z_first"]:
        if strategy in data_dict:
            df = data_dict[strategy]
            ax4.plot(
                df["injection_rate"],
                df["throughput"],
                marker=markers[strategy],
                color=colors[strategy],
                label=labels[strategy],
                linewidth=2,
                markersize=4,
            )
    ax4.set_xlabel("Injection Rate")
    ax4.set_ylabel("Throughput (packets/cycle)")
    ax4.set_title("Throughput vs Injection Rate")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Adjust layout and save
    plt.tight_layout()
    output_file = os.path.join(
        output_dir, f"{pattern}_tie_breaking_comparison.pdf"
    )
    plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

    return output_file


def generate_tie_breaking_summary(data_dict, pattern):
    """
    Generate summary statistics for tie-breaking strategies
    """
    summary_stats = []

    for strategy in ["x_first", "uniform", "z_first"]:
        if strategy not in data_dict:
            continue

        df = data_dict[strategy]

        # Find maximum throughput
        max_throughput = df["throughput"].max()

        # Find latency at 50% of max throughput
        target_throughput = max_throughput * 0.5
        latency_at_50pct = np.interp(
            target_throughput, df["throughput"], df["avg_latency"]
        )

        # Find average hops at 50% of max throughput
        hops_at_50pct = np.interp(
            target_throughput, df["throughput"], df["avg_hops"]
        )

        stats = {
            "strategy": strategy,
            "max_throughput": max_throughput,
            "latency_at_50pct": latency_at_50pct,
            "hops_at_50pct": hops_at_50pct,
        }
        summary_stats.append(stats)

    return summary_stats


def main():
    """
    Main function to generate tie-breaking comparison plots
    """
    # Define directories
    base_dir = "./"
    results_dir = os.path.join(base_dir, "results", "adaptive_tie_breaking")
    output_dir = os.path.join(base_dir, "results", "adaptive_tie_breaking")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Check if results directory exists
    if not os.path.exists(results_dir):
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run the tie-breaking experiments first.")
        return

    print("Generating adaptive tie-breaking comparison plots...")
    print("=" * 60)

    # Load data for bit_reverse pattern
    pattern = "bit_reverse"
    print(f"\nProcessing {pattern} pattern...")

    data_dict = load_tie_breaking_data(results_dir, pattern)

    if data_dict is None or len(data_dict) == 0:
        print(f"No valid data found for {pattern}")
        return

    # Generate comparison plot
    try:
        output_file = create_tie_breaking_comparison_plot(
            data_dict, pattern, output_dir
        )
        print(f"✓ Created: {output_file}")

        # Generate summary statistics
        summary_stats = generate_tie_breaking_summary(data_dict, pattern)

        if summary_stats:
            # Save summary to CSV
            summary_df = pd.DataFrame(summary_stats)
            summary_file = os.path.join(
                output_dir, f"{pattern}_tie_breaking_summary.csv"
            )
            summary_df.to_csv(summary_file, index=False)
            print(f"✓ Summary statistics saved to: {summary_file}")

            # Print summary
            print(f"\n" + "=" * 60)
            print("TIE-BREAKING STRATEGY PERFORMANCE SUMMARY")
            print("=" * 60)
            print(f"Pattern: {pattern.replace('_', ' ').title()}")
            print("-" * 60)

            # Find best performing strategy
            best_throughput = max(
                summary_stats, key=lambda x: x["max_throughput"]
            )
            best_latency = min(
                summary_stats, key=lambda x: x["latency_at_50pct"]
            )
            best_hops = min(summary_stats, key=lambda x: x["hops_at_50pct"])

            for stat in summary_stats:
                strategy_name = stat["strategy"].replace("_", "-")
                print(f"\n{strategy_name.upper()}:")
                print(
                    f"  Max Throughput: {stat['max_throughput']:.6f} packets/cycle"
                )
                print(
                    f"  Latency (50% load): {stat['latency_at_50pct']:.2f} ticks"
                )
                print(f"  Avg Hops (50% load): {stat['hops_at_50pct']:.2f}")

                # Mark best performers
                markers = []
                if stat["strategy"] == best_throughput["strategy"]:
                    markers.append("🏆 Best Throughput")
                if stat["strategy"] == best_latency["strategy"]:
                    markers.append("⚡ Best Latency")
                if stat["strategy"] == best_hops["strategy"]:
                    markers.append("📏 Shortest Path")

                if markers:
                    print(f"  {' | '.join(markers)}")

            # Performance comparison
            x_first_stats = next(
                (s for s in summary_stats if s["strategy"] == "x_first"), None
            )
            if x_first_stats:
                print(f"\n" + "-" * 60)
                print("PERFORMANCE COMPARISON (vs X-First baseline):")
                print("-" * 60)

                for stat in summary_stats:
                    if stat["strategy"] == "x_first":
                        continue

                    throughput_improvement = (
                        (
                            stat["max_throughput"]
                            - x_first_stats["max_throughput"]
                        )
                        / x_first_stats["max_throughput"]
                    ) * 100
                    latency_improvement = (
                        (
                            x_first_stats["latency_at_50pct"]
                            - stat["latency_at_50pct"]
                        )
                        / x_first_stats["latency_at_50pct"]
                    ) * 100

                    strategy_name = stat["strategy"].replace("_", "-").upper()
                    print(f"\n{strategy_name}:")
                    print(
                        f"  Throughput change: {throughput_improvement:+.2f}%"
                    )
                    print(
                        f"  Latency improvement: {latency_improvement:+.2f}%"
                    )

    except Exception as e:
        print(f"✗ Error creating plot for {pattern}: {e}")

    print(f"\n" + "=" * 60)
    print(f"Tie-breaking analysis complete!")
    print(f"Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
