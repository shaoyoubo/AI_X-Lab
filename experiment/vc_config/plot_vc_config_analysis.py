#!/usr/bin/env python3
"""
Virtual Channel Configuration Analysis Script for Lab4 experiment
Compares different VC configurations in adaptive routing
Generates multiple 2x2 subplot figures for different comparison groups
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


def load_data(results_dir, pattern, vc_configs):
    """
    Load data for all VC configurations
    """
    data_dict = {}

    for vcs_per_vnet, escape_vcs in vc_configs:
        filename = (
            f"{pattern}_vcs{vcs_per_vnet}_escape{escape_vcs}_results.csv"
        )
        filepath = os.path.join(results_dir, filename)

        try:
            df = pd.read_csv(filepath)
            # Filter out failed runs
            df = df[df["throughput"] != "FAILED"]
            df = df.apply(pd.to_numeric, errors="coerce")
            df = df.dropna()

            if len(df) > 0:
                data_dict[(vcs_per_vnet, escape_vcs)] = df
                adaptive_vcs = vcs_per_vnet - escape_vcs
                print(
                    f"✓ Loaded data for VC({vcs_per_vnet},{escape_vcs}) [Adaptive:{adaptive_vcs}]: {len(df)} data points"
                )
            else:
                print(f"✗ No valid data for VC({vcs_per_vnet},{escape_vcs})")

        except FileNotFoundError:
            print(f"✗ File not found: {filepath}")
        except Exception as e:
            print(f"✗ Error loading {filepath}: {e}")

    return data_dict


def create_comparison_plot(
    data_dict, configs, group_name, pattern, output_dir
):
    """
    Create a 2x2 comparison plot for one VC configuration group
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        f"VC Configuration Analysis: {group_name}\n"
        f'Traffic Pattern: {pattern.replace("_", " ").title()}',
        fontsize=14,
        fontweight="bold",
    )

    # Special handling for Group 5 (Combined Group 1 + Group 4)
    is_combined_group = "Combined" in group_name
    
    if is_combined_group:
        # Define colors for Group 1 (Fixed Escape VCs) and Group 4 (All Escape VCs)
        group1_configs = [(1, 1), (2, 1), (4, 1), (8, 1)]
        group4_configs = [(2, 2), (4, 4), (8, 8)]  # (1,1) is shared
        
        group1_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]  # Blue tones
        group4_colors = ["#ff7f0e", "#2ca02c", "#d62728"]  # Purple tones
        group1_markers = ["o", "s", "^", "d"]
        group4_markers = ["v", "<", ">"]
        
        colors = []
        markers = []
        linestyles = []
        
        for config in configs:
            if config in group1_configs:
                idx = group1_configs.index(config)
                colors.append(group1_colors[idx])
                markers.append(group1_markers[idx])
                linestyles.append("-")  # Solid for Group 1
            elif config in group4_configs:
                idx = group4_configs.index(config)
                colors.append(group4_colors[idx])
                markers.append(group4_markers[idx])
                linestyles.append("--")  # Dashed for Group 4
    else:
        # Original color scheme for other groups
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
        linestyles = ["-", "--", "-.", ":", "-", "--"]
        markers = ["o", "s", "^", "d", "v", "<"]

    # Plot 1: Latency vs Throughput
    ax1 = axes[0, 0]
    for i, (vcs_per_vnet, escape_vcs) in enumerate(configs):
        if (vcs_per_vnet, escape_vcs) in data_dict:
            df = data_dict[(vcs_per_vnet, escape_vcs)]
            adaptive_vcs = vcs_per_vnet - escape_vcs
            
            if is_combined_group:
                # Add group identifier for combined plot
                if (vcs_per_vnet, escape_vcs) in [(1, 1), (2, 1), (4, 1), (8, 1)]:
                    label = f"G1: VC({vcs_per_vnet},{escape_vcs}) [A:{adaptive_vcs}]"
                else:
                    label = f"G4: VC({vcs_per_vnet},{escape_vcs}) [A:{adaptive_vcs}]"
            else:
                label = f"VC({vcs_per_vnet},{escape_vcs}) [A:{adaptive_vcs}]"

            ax1.plot(
                df["throughput"],
                df["avg_latency"],
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                marker=markers[i % len(markers)],
                label=label,
                linewidth=2,
                markersize=4,
            )

    ax1.set_xlabel("Throughput (packets/cycle)")
    ax1.set_ylabel("Average Latency (ticks)")
    ax1.set_title("Latency vs Throughput")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Latency vs Throughput (Log Scale)
    ax2 = axes[0, 1]
    for i, (vcs_per_vnet, escape_vcs) in enumerate(configs):
        if (vcs_per_vnet, escape_vcs) in data_dict:
            df = data_dict[(vcs_per_vnet, escape_vcs)]
            adaptive_vcs = vcs_per_vnet - escape_vcs
            
            if is_combined_group:
                if (vcs_per_vnet, escape_vcs) in [(1, 1), (2, 1), (4, 1), (8, 1)]:
                    label = f"G1: VC({vcs_per_vnet},{escape_vcs})"
                else:
                    label = f"G4: VC({vcs_per_vnet},{escape_vcs})"
            else:
                label = f"VC({vcs_per_vnet},{escape_vcs})"

            ax2.plot(
                df["throughput"],
                df["avg_latency"],
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                marker=markers[i % len(markers)],
                label=label,
                linewidth=2,
                markersize=4,
            )

    ax2.set_xlabel("Throughput (packets/cycle)")
    ax2.set_ylabel("Average Latency (ticks)")
    ax2.set_yscale("log")
    ax2.set_title("Latency vs Throughput (Log Scale)")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Plot 3: Average Hops vs Throughput
    ax3 = axes[1, 0]
    for i, (vcs_per_vnet, escape_vcs) in enumerate(configs):
        if (vcs_per_vnet, escape_vcs) in data_dict:
            df = data_dict[(vcs_per_vnet, escape_vcs)]
            adaptive_vcs = vcs_per_vnet - escape_vcs
            
            if is_combined_group:
                if (vcs_per_vnet, escape_vcs) in [(1, 1), (2, 1), (4, 1), (8, 1)]:
                    label = f"G1: VC({vcs_per_vnet},{escape_vcs})"
                else:
                    label = f"G4: VC({vcs_per_vnet},{escape_vcs})"
            else:
                label = f"VC({vcs_per_vnet},{escape_vcs})"

            ax3.plot(
                df["throughput"],
                df["avg_hops"],
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                marker=markers[i % len(markers)],
                label=label,
                linewidth=2,
                markersize=4,
            )

    ax3.set_xlabel("Throughput (packets/cycle)")
    ax3.set_ylabel("Average Hops")
    ax3.set_title("Average Hops vs Throughput")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Plot 4: Throughput vs Injection Rate
    ax4 = axes[1, 1]
    for i, (vcs_per_vnet, escape_vcs) in enumerate(configs):
        if (vcs_per_vnet, escape_vcs) in data_dict:
            df = data_dict[(vcs_per_vnet, escape_vcs)]
            adaptive_vcs = vcs_per_vnet - escape_vcs
            
            if is_combined_group:
                if (vcs_per_vnet, escape_vcs) in [(1, 1), (2, 1), (4, 1), (8, 1)]:
                    label = f"G1: VC({vcs_per_vnet},{escape_vcs})"
                else:
                    label = f"G4: VC({vcs_per_vnet},{escape_vcs})"
            else:
                label = f"VC({vcs_per_vnet},{escape_vcs})"

            ax4.plot(
                df["injection_rate"],
                df["throughput"],
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                marker=markers[i % len(markers)],
                label=label,
                linewidth=2,
                markersize=4,
            )

    ax4.set_xlabel("Injection Rate")
    ax4.set_ylabel("Throughput (packets/cycle)")
    ax4.set_title("Throughput vs Injection Rate")
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    # Adjust layout and save
    plt.tight_layout()
    group_filename = (
        group_name.lower()
        .replace(" ", "_")
        .replace(":", "")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "_")
    )
    output_file = os.path.join(
        output_dir, f"{pattern}_vc_config_{group_filename}.pdf"
    )
    plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
    plt.close()

    return output_file


def generate_summary_stats(data_dict, configs, group_name):
    """
    Generate summary statistics for VC configuration comparison
    """
    stats = []

    for vcs_per_vnet, escape_vcs in configs:
        if (vcs_per_vnet, escape_vcs) not in data_dict:
            continue

        df = data_dict[(vcs_per_vnet, escape_vcs)]
        if len(df) == 0:
            continue

        adaptive_vcs = vcs_per_vnet - escape_vcs
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
                "group": group_name,
                "vcs_per_vnet": vcs_per_vnet,
                "escape_vcs": escape_vcs,
                "adaptive_vcs": adaptive_vcs,
                "escape_ratio": escape_vcs / vcs_per_vnet,
                "max_throughput": max_throughput,
                "min_latency": min_latency,
                "latency_at_50pct_throughput": latency_at_50pct,
                "avg_hops_mean": avg_hops_mean,
            }
        )

    return stats


def main():
    """
    Main function to generate VC configuration analysis plots
    """
    # Define directories
    base_dir = "./"
    results_dir = os.path.join(base_dir, "results", "vc_config")
    output_dir = os.path.join(base_dir, "results", "vc_config")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Traffic pattern (only bit_reverse)
    pattern = "bit_reverse"

    # Define comparison groups
    comparison_groups = {
        "Group1_Fixed_Escape_VCs": {
            "name": "Group 1: Fixed Escape VCs (escape=1)",
            "configs": [(1, 1), (2, 1), (4, 1), (8, 1)],
            "description": "Impact of increasing total VCs with fixed escape VCs",
        },
        "Group2_Fixed_Total_VCs_4": {
            "name": "Group 2: Fixed Total VCs (total=4)",
            "configs": [(4, 1), (4, 2), (4, 3), (4, 4)],
            "description": "Impact of escape VC ratio with 4 total VCs",
        },
        "Group3_Fixed_Total_VCs_8": {
            "name": "Group 3: Fixed Total VCs (total=8)",
            "configs": [(8, 1), (8, 2), (8, 4), (8, 8)],
            "description": "Impact of escape VC ratio with 8 total VCs",
        },
        "Group4_All_Escape_VCs": {
            "name": "Group 4: All Escape VCs (adaptive=0)",
            "configs": [(1, 1), (2, 2), (4, 4), (8, 8)],
            "description": "Pure deterministic routing with different VC counts",
        },
        "Group5_Combined_1_and_4": {
            "name": "Group 5: Combined Analysis (Group 1 + Group 4)",
            "configs": [(1, 1), (2, 1), (4, 1), (8, 1), (2, 2), (4, 4), (8, 8)],
            "description": "Fixed escape VCs vs All escape VCs comparison",
        },
    }

    # All VC configurations for data loading
    all_configs = set()
    for group_data in comparison_groups.values():
        all_configs.update(group_data["configs"])
    all_configs = list(all_configs)

    # Check if results directory exists
    if not os.path.exists(results_dir):
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run the VC configuration experiments first.")
        return

    print("Generating VC configuration analysis plots...")
    print("=" * 50)
    print(f"Pattern: {pattern}")
    print(f"Total configurations to analyze: {len(all_configs)}")
    print("")

    # Load all data
    data_dict = load_data(results_dir, pattern, all_configs)

    if not data_dict:
        print("Error: No data loaded successfully!")
        return

    print(f"\nSuccessfully loaded data for {len(data_dict)} VC configurations")

    # Generate plots for each comparison group
    all_stats = []
    successful_plots = 0

    for group_key, group_data in comparison_groups.items():
        print(f"\n" + "=" * 50)
        print(f"Processing {group_data['name']}")
        print(f"Description: {group_data['description']}")
        print("=" * 50)

        try:
            output_file = create_comparison_plot(
                data_dict,
                group_data["configs"],
                group_data["name"],
                pattern,
                output_dir,
            )
            print(f"✓ Created plot: {output_file}")
            successful_plots += 1

            # Generate statistics for this group
            stats = generate_summary_stats(
                data_dict, group_data["configs"], group_data["name"]
            )
            all_stats.extend(stats)

        except Exception as e:
            print(f"✗ Error creating plot for {group_data['name']}: {e}")

    # Save summary statistics
    if all_stats:
        stats_df = pd.DataFrame(all_stats)
        stats_file = os.path.join(
            output_dir, f"{pattern}_vc_config_summary.csv"
        )
        stats_df.to_csv(stats_file, index=False)
        print(f"\n✓ Summary statistics saved to: {stats_file}")

        # Print summary by group
        print("\n" + "=" * 50)
        print("VC CONFIGURATION ANALYSIS SUMMARY")
        print("=" * 50)

        for group_key, group_data in comparison_groups.items():
            group_stats = [
                s for s in all_stats if s["group"] == group_data["name"]
            ]
            if group_stats:
                print(f"\n{group_data['name']}:")
                print(f"  {group_data['description']}")
                for stat in group_stats:
                    print(
                        f"  VC({stat['vcs_per_vnet']},{stat['escape_vcs']}) [A:{stat['adaptive_vcs']}]: "
                        f"MaxThroughput={stat['max_throughput']:.6f}, "
                        f"MinLatency={stat['min_latency']:.2f}"
                    )

    print(f"\n" + "=" * 50)
    print("VC configuration analysis completed!")
    print(
        f"Successfully generated {successful_plots} out of {len(comparison_groups)} plots"
    )
    print(f"Output directory: {output_dir}")
    print("Generated files:")
    for group_key, group_data in comparison_groups.items():
        group_filename = (
            group_data["name"]
            .lower()
            .replace(" ", "_")
            .replace(":", "")
            .replace("(", "")
            .replace(")", "")
            .replace(",", "_")
        )
        print(f"  - {pattern}_vc_config_{group_filename}.pdf")
    print("=" * 50)


if __name__ == "__main__":
    main()
