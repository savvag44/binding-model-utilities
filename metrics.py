#!/usr/bin/env python3
# metrics.py rfscore_boltz_1x_FEP_reformat.csv -g FEP_benchmark.csv
import argparse
import pandas as pd
from calc_metrics import MetricCalculator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", help="path to CSV with columns: key,pred,pk")
    parser.add_argument("-g", "--group_lookup", help="CSV with system_id→group_id mapping")
    parser.add_argument("--n_iterations", type=int, default=500)
    parser.add_argument("--n_min",        type=int, default=10)
    args = parser.parse_args()

    df = pd.read_csv(args.csv_file)
    if args.group_lookup:
        lookup = pd.read_csv(args.group_lookup, usecols=["system_id","group_id"])
        df = df.merge(lookup, left_on="key", right_on="system_id", how="left")
        groups = df["group_id"].tolist()
    else:
        groups = None

    y_pred = df["pred"].tolist()
    y_true = df["pk"].tolist()

    print(f"Calculating metrics and performing bootstrapping with {args.n_iterations} iterations")
    mc = MetricCalculator(y_pred, y_true, groups,
                          n_min=args.n_min,
                          n_iterations=args.n_iterations)
    m = mc.all_metrics()

    print("\nOverall metrics:")
    print(f"- RMSE:    {m['rmse'][0]:.7f} ± {m['rmse'][1]:.7f}")
    print(f"- Pearson: {m['pearson'][0]:.7f} ± {m['pearson'][1]:.7f}")
    print(f"- Kendall: {m['kendall'][0]:.7f} ± {m['kendall'][1]:.7f}")
    print(f"- Spearman:{m['spearman'][0]:.7f} ± {m['spearman'][1]:.7f}")
    print(f"- C-index: {m['c_index'][0]:.7f} ± {m['c_index'][1]:.7f}")

if __name__ == "__main__":
    main()
