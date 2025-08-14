#!/usr/bin/env python3
# python3 metric_ensembles.py /documents/rfscore_python/hiqbind_boltz -g FEP_benchmark.csv
import argparse
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from calc_metrics import MetricCalculator

def find_model_dirs(base_dir):
   """Find all model{n} subdirectories."""
   return sorted([d for d in base_dir.iterdir() 
                  if d.is_dir() and d.name.startswith('model') 
                  and d.name[5:].isdigit()])

def find_csv_in_model(model_dir):
   """Find the CSV file in model{n}/data/results/"""
   results_dir = model_dir / 'data' / 'results'
   if not results_dir.exists():
       return None
   csv_files = list(results_dir.glob('*.csv'))
   return csv_files[0] if csv_files else None

def calculate_metrics(df, group_lookup_file, n_iterations, n_min):
   """Calculate metrics for a dataframe."""
   if group_lookup_file and Path(group_lookup_file).exists():
       lookup = pd.read_csv(group_lookup_file, usecols=["system_id","group_id"])
       df = df.merge(lookup, left_on="key", right_on="system_id", how="left")
       groups = df["group_id"].tolist()
   else:
       groups = None

   mc = MetricCalculator(df["pred"].tolist(), df["pk"].tolist(), groups,
                         n_min=n_min, n_iterations=n_iterations)
   return mc.all_metrics()

def format_metrics(metrics):
   """Format metrics dict for output."""
   lines = []
   for name, (value, uncertainty, _) in metrics.items():
       lines.append(f"- {name.upper():<9} {value:.7f} ± {uncertainty:.7f}")
   return '\n'.join(lines)

def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("base_dir", type=Path, help="Base directory containing model{n} subdirs")
   parser.add_argument("-e", "--ensemble_file", type=Path, 
                       help="Output ensemble CSV file (default: base_dir/ensemble.csv)")
   parser.add_argument("-o", "--output_file", type=Path,
                       help="Output metrics log file (default: base_dir/metrics_[un]weighted.log)")
   parser.add_argument("-g", "--group_lookup", help="CSV with system_id→group_id mapping")
   parser.add_argument("--n_iterations", type=int, default=500)
   parser.add_argument("--n_min", type=int, default=10)
   args = parser.parse_args()

   # Set defaults
   if not args.ensemble_file:
       args.ensemble_file = args.base_dir / "ensemble.csv"
   if not args.output_file:
       # Default filename based on whether groups are used
       if args.group_lookup:
           args.output_file = args.base_dir / "metrics_weighted.log"
       else:
           args.output_file = args.base_dir / "metrics_unweighted.log"

   # Find model directories
   model_dirs = find_model_dirs(args.base_dir)
   if not model_dirs:
       print(f"No model directories found in {args.base_dir}")
       return

   # Collect all model predictions
   all_dfs = []
   model_results = {}
   
   for model_dir in model_dirs:
       csv_file = find_csv_in_model(model_dir)
       if not csv_file:
           print(f"Warning: No CSV found in {model_dir}/data/results/, skipping")
           continue
       
       df = pd.read_csv(csv_file)
       all_dfs.append(df)
       
       # Calculate individual model metrics
       metrics = calculate_metrics(df, args.group_lookup, args.n_iterations, args.n_min)
       model_results[model_dir.name] = metrics

   if not all_dfs:
       print("No valid model data found")
       return

   # Create ensemble
   ensemble_df = all_dfs[0][['key', 'pk']].copy()
   pred_matrix = np.column_stack([df['pred'].values for df in all_dfs])
   ensemble_df['pred'] = pred_matrix.mean(axis=1)
   ensemble_df.to_csv(args.ensemble_file, index=False)
   
   # Calculate ensemble metrics
   ensemble_metrics = calculate_metrics(ensemble_df, args.group_lookup, 
                                        args.n_iterations, args.n_min)

   # Write output
   with open(args.output_file, 'w') as f:
       # Header with command and weighting info
       f.write(f"Command: {' '.join(sys.argv)}\n")
       f.write(f"Metrics type: {'WEIGHTED' if args.group_lookup else 'UNWEIGHTED'}\n")
       if args.group_lookup:
           f.write(f"Group lookup file: {args.group_lookup}\n")
       f.write(f"\nMetrics for models in {args.base_dir}\n")
       f.write(f"{'='*60}\n\n")
       
       # Individual models
       for model_name, metrics in model_results.items():
           f.write(f"{model_name}:\n")
           f.write(format_metrics(metrics))
           f.write("\n\n")
       
       # Ensemble
       f.write(f"Ensemble ({len(all_dfs)} models):\n")
       f.write(format_metrics(ensemble_metrics))
       f.write(f"\n\nEnsemble predictions saved to: {args.ensemble_file}\n")

   print(f"Results written to {args.output_file}")

if __name__ == "__main__":
   main()