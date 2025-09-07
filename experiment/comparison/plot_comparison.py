#!/usr/bin/env python3
"""
Comparison script for Lab4 experiment
Compares three configurations:
1. Baseline: Deterministic routing (routing=3) on 3D Torus
2. Baseline_2: Mesh_XYZ topology
3. Synthetic: Adaptive routing (routing=4) on 3D Torus
Generates 8 PDF files, one for each synthetic traffic pattern
Each PDF contains 2x2 subplots comparing the three configurations
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


def load_data(synthetic_dir, baseline_dir, baseline2_dir, pattern):
    """
    Load data for all three configurations for a specific traffic pattern
    """
    synthetic_file = os.path.join(synthetic_dir, f"{pattern}_results.csv")
    baseline_file = os.path.join(
        baseline_dir, f"{pattern}_baseline_results.csv"
    )
    baseline2_file = os.path.join(
        baseline2_dir, f"{pattern}_baseline_2_results.csv"
    )

    try:
        # Load synthetic (adaptive routing on 3D Torus) data
        df_adaptive = pd.read_csv(synthetic_file)
        df_adaptive = df_adaptive[df_adaptive["throughput"] != "FAILED"]
        df_adaptive = df_adaptive.apply(pd.to_numeric, errors="coerce")
        df_adaptive = df_adaptive.dropna()

        # Load baseline (deterministic routing on 3D Torus) data
        df_deterministic = pd.read_csv(baseline_file)
        df_deterministic = df_deterministic[
            df_deterministic["throughput"] != "FAILED"
        ]
        df_deterministic = df_deterministic.apply(
            pd.to_numeric, errors="coerce"
        )
        df_deterministic = df_deterministic.dropna()

        # Load baseline_2 (Mesh_XYZ) data
        df_mesh = pd.read_csv(baseline2_file)
        df_mesh = df_mesh[df_mesh["throughput"] != "FAILED"]
        df_mesh = df_mesh.apply(pd.to_numeric, errors="coerce")
        df_mesh = df_mesh.dropna()

        return df_deterministic, df_mesh, df_adaptive

    except FileNotFoundError as e:
        print(f"Error: Could not find data files for {pattern}")
        print(
            f"Looking for: {synthetic_file}, {baseline_file}, {baseline2_file}"
        )
        return None, None, None
    except Exception as e:
        print(f"Error loading data for {pattern}: {e}")
        return None, None, None


def create_comparison_plot(
    df_deterministic, df_mesh, df_adaptive, pattern, output_dir
):
    """
    Create a 2x2 comparison plot for one traffic pattern with three configurations
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        f'Performance Comparison: {pattern.replace("_", " ").title()}\n'
        f"Deterministic 3D Torus vs Mesh_XYZ vs Adaptive 3D Torus",
        fontsize=14,
        fontweight="bold",
    )

    # Colors for the three configurations
    color_deterministic = "#1f77b4"  # Blue
    color_mesh = "#ff7f0e"  # Orange
    color_adaptive = "#2ca02c"  # Green

    # Plot 1: Latency vs Throughput
    ax1 = axes[0, 0]
    ax1.plot(
        df_deterministic["throughput"],
        df_deterministic["avg_latency"],
        "o-",
        color=color_deterministic,
        label="3D Torus (Deterministic)",
        linewidth=2,
        markersize=4,
    )
    ax1.plot(
        df_mesh["throughput"],
        df_mesh["avg_latency"],
        "^-",
        color=color_mesh,
        label="Mesh_XYZ",
        linewidth=2,
        markersize=4,
    )
    ax1.plot(
        df_adaptive["throughput"],
        df_adaptive["avg_latency"],
        "s-",
        color=color_adaptive,
        label="3D Torus (Adaptive)",
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
    ax2.plot(
        df_deterministic["throughput"],
        df_deterministic["avg_latency"],
        "o-",
        color=color_deterministic,
        label="3D Torus (Deterministic)",
        linewidth=2,
        markersize=4,
    )
    ax2.plot(
        df_mesh["throughput"],
        df_mesh["avg_latency"],
        "^-",
        color=color_mesh,
        label="Mesh_XYZ",
        linewidth=2,
        markersize=4,
    )
    ax2.plot(
        df_adaptive["throughput"],
        df_adaptive["avg_latency"],
        "s-",
        color=color_adaptive,
        label="3D Torus (Adaptive)",
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
    ax3.plot(
        df_deterministic["throughput"],
        df_deterministic["avg_hops"],
        "o-",
        color=color_deterministic,
        label="3D Torus (Deterministic)",
        linewidth=2,
        markersize=4,
    )
    ax3.plot(
        df_mesh["throughput"],
        df_mesh["avg_hops"],
        "^-",
        color=color_mesh,
        label="Mesh_XYZ",
        linewidth=2,
        markersize=4,
    )
    ax3.plot(
        df_adaptive["throughput"],
        df_adaptive["avg_hops"],
        "s-",
        color=color_adaptive,
        label="3D Torus (Adaptive)",
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
    ax4.plot(
        df_deterministic["injection_rate"],
        df_deterministic["throughput"],
        "o-",
        color=color_deterministic,
        label="3D Torus (Deterministic)",
        linewidth=2,
        markersize=4,
    )
    ax4.plot(
        df_mesh["injection_rate"],
        df_mesh["throughput"],
        "^-",
        color=color_mesh,
        label="Mesh_XYZ",
        linewidth=2,
        markersize=4,
    )
    ax4.plot(
        df_adaptive["injection_rate"],
        df_adaptive["throughput"],
        "s-",
        color=color_adaptive,
        label="3D Torus (Adaptive)",
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
    output_file = os.path.join(output_dir, f"{pattern}_comparison.pdf")
    plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

    return output_file


def generate_summary_stats(df_deterministic, df_mesh, df_adaptive, pattern):
    """
    Generate summary statistics for comparison of three configurations
    """
    stats = {}

    # Find maximum throughput for each configuration
    max_throughput_det = df_deterministic["throughput"].max()
    max_throughput_mesh = df_mesh["throughput"].max()
    max_throughput_adap = df_adaptive["throughput"].max()

    # Find latency at 50% of max throughput
    target_throughput_det = max_throughput_det * 0.5
    target_throughput_mesh = max_throughput_mesh * 0.5
    target_throughput_adap = max_throughput_adap * 0.5

    # Interpolate latency at target throughput
    latency_det_50 = np.interp(
        target_throughput_det,
        df_deterministic["throughput"],
        df_deterministic["avg_latency"],
    )
    latency_mesh_50 = np.interp(
        target_throughput_mesh,
        df_mesh["throughput"],
        df_mesh["avg_latency"],
    )
    latency_adap_50 = np.interp(
        target_throughput_adap,
        df_adaptive["throughput"],
        df_adaptive["avg_latency"],
    )

    stats = {
        "pattern": pattern,
        "max_throughput_deterministic": max_throughput_det,
        "max_throughput_mesh": max_throughput_mesh,
        "max_throughput_adaptive": max_throughput_adap,
        "throughput_improvement_adaptive_vs_det": (
            (max_throughput_adap - max_throughput_det) / max_throughput_det
        )
        * 100,
        "throughput_improvement_adaptive_vs_mesh": (
            (max_throughput_adap - max_throughput_mesh) / max_throughput_mesh
        )
        * 100,
        "latency_at_50pct_deterministic": latency_det_50,
        "latency_at_50pct_mesh": latency_mesh_50,
        "latency_at_50pct_adaptive": latency_adap_50,
        "latency_improvement_adaptive_vs_det": (
            (latency_det_50 - latency_adap_50) / latency_det_50
        )
        * 100,
        "latency_improvement_adaptive_vs_mesh": (
            (latency_mesh_50 - latency_adap_50) / latency_mesh_50
        )
        * 100,
    }

    return stats


def main():
    """
    Main function to generate all comparison plots
    """
    # Define directories - base_dir is current folder (experiment/comparison)
    base_dir = "./"
    synthetic_dir = os.path.join(base_dir, "results", "synthetic")
    baseline_dir = os.path.join(base_dir, "results", "baseline")
    baseline2_dir = os.path.join(base_dir, "results", "baseline_2")
    output_dir = os.path.join(base_dir, "results", "comparison")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Traffic patterns to compare
    traffic_patterns = [
        "uniform_random",
        "shuffle",
        "transpose",
        "tornado",
        "neighbor",
        "bit_complement",
        "bit_reverse",
        "bit_rotation",
    ]

    # Check if data directories exist
    if not os.path.exists(synthetic_dir):
        print(f"Error: Synthetic results directory not found: {synthetic_dir}")
        print("Please run the synthetic experiments first.")
        return

    if not os.path.exists(baseline_dir):
        print(f"Error: Baseline results directory not found: {baseline_dir}")
        print("Please run the baseline experiments first.")
        return

    if not os.path.exists(baseline2_dir):
        print(
            f"Error: Baseline_2 results directory not found: {baseline2_dir}"
        )
        print("Please run the baseline_2 experiments first.")
        return

    print("Generating performance comparison plots...")
    print("=" * 50)

    all_stats = []
    successful_plots = 0

    for pattern in traffic_patterns:
        print(f"\nProcessing {pattern}...")

        # Load data for all three configurations
        df_deterministic, df_mesh, df_adaptive = load_data(
            synthetic_dir, baseline_dir, baseline2_dir, pattern
        )

        if df_deterministic is None or df_mesh is None or df_adaptive is None:
            print(f"Skipping {pattern} due to data loading errors")
            continue

        if (
            len(df_deterministic) == 0
            or len(df_mesh) == 0
            or len(df_adaptive) == 0
        ):
            print(f"Skipping {pattern} due to empty data")
            continue

        # Generate comparison plot
        try:
            output_file = create_comparison_plot(
                df_deterministic, df_mesh, df_adaptive, pattern, output_dir
            )
            print(f"✓ Created: {output_file}")
            successful_plots += 1

            # Generate statistics
            stats = generate_summary_stats(
                df_deterministic, df_mesh, df_adaptive, pattern
            )
            all_stats.append(stats)

        except Exception as e:
            print(f"✗ Error creating plot for {pattern}: {e}")

    # Save summary statistics
    if all_stats:
        stats_df = pd.DataFrame(all_stats)
        stats_file = os.path.join(output_dir, "comparison_summary.csv")
        stats_df.to_csv(stats_file, index=False)
        print(f"\n✓ Summary statistics saved to: {stats_file}")

        # Print summary
        print("\n" + "=" * 50)
        print("PERFORMANCE SUMMARY")
        print("=" * 50)
        for stat in all_stats:
            print(f"\n{stat['pattern'].replace('_', ' ').title()}:")
            print(
                f"  Adaptive vs Deterministic Throughput: {stat['throughput_improvement_adaptive_vs_det']:+.1f}%"
            )
            print(
                f"  Adaptive vs Mesh Throughput: {stat['throughput_improvement_adaptive_vs_mesh']:+.1f}%"
            )
            print(
                f"  Adaptive vs Deterministic Latency: {stat['latency_improvement_adaptive_vs_det']:+.1f}%"
            )
            print(
                f"  Adaptive vs Mesh Latency: {stat['latency_improvement_adaptive_vs_mesh']:+.1f}%"
            )

    print(f"\n" + "=" * 50)
    print(f"Comparison complete!")
    print(
        f"Successfully generated {successful_plots} out of {len(traffic_patterns)} plots"
    )
    print(f"Output directory: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
