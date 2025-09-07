#!/bin/bash
# Lab4 Complete Experiment Runner

echo "Running complete Lab4 experiment pipeline..."

# Run baseline experiments
chmod +x experiment/baseline/run_baseline_experiments.sh
bash experiment/baseline/run_baseline_experiments.sh

# Run baseline_2 experiments
chmod +x experiment/baseline_2/run_baseline_2_experiments.sh
bash experiment/baseline_2/run_baseline_2_experiments.sh

# Run synthetic experiments
chmod +x experiment/synthetic/run_synthetic_experiments.sh
bash experiment/synthetic/run_synthetic_experiments.sh

# Generate comparison plots
chmod +x experiment/comparison/plot_comparison.py
python3 experiment/comparison/plot_comparison.py

echo "All experiments completed!"
