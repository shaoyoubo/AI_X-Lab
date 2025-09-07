#!/bin/bash
# Lab4 Parameter Study Experiment Runner

echo "Running complete Lab4 parameter study pipeline..."

# Run adaptive tie-breaking experiments
chmod +x experiment/adaptive_tie_breaking/run_tie_breaking_experiments.sh
bash experiment/adaptive_tie_breaking/run_tie_breaking_experiments.sh

# Generate tie-breaking analysis plots
chmod +x experiment/adaptive_tie_breaking/plot_tie_breaking_analysis.py
python3 experiment/adaptive_tie_breaking/plot_tie_breaking_analysis.py

# Run distance coefficient experiments
chmod +x experiment/distance_coefficient/run_distance_coefficient_experiments.sh
bash experiment/distance_coefficient/run_distance_coefficient_experiments.sh

# Generate distance coefficient analysis plots
chmod +x experiment/distance_coefficient/plot_distance_coefficient_analysis.py
python3 experiment/distance_coefficient/plot_distance_coefficient_analysis.py

# Run injection virtual network experiments
chmod +x experiment/inj_vnet/run_inj_vnet_experiments.sh
bash experiment/inj_vnet/run_inj_vnet_experiments.sh

# Generate injection virtual network analysis plots
chmod +x experiment/inj_vnet/plot_inj_vnet_analysis.py
python3 experiment/inj_vnet/plot_inj_vnet_analysis.py

# Run virtual channel configuration experiments
chmod +x experiment/vc_config/run_vc_config_experiments.sh
bash experiment/vc_config/run_vc_config_experiments.sh

# Generate virtual channel configuration analysis plots
chmod +x experiment/vc_config/plot_vc_config_analysis.py
python3 experiment/vc_config/plot_vc_config_analysis.py

echo "All parameter study experiments completed!"
