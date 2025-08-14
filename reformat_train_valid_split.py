import pandas as pd
import os
import argparse

"""
Reformat HiQBind CSV, strip paths relative to a root directory, and split into train/validation files.
Usage:
    python3 reformat_train_valid_split.py input.csv root_dir output_name
Creates:
    output_name_train.csv
    output_name_validation.csv
"""

def strip_prefix(path_str: str, root_dir: str) -> str:
    abs_path = os.path.abspath(path_str)
    root = os.path.abspath(root_dir)
    prefix = root + os.sep
    if abs_path.startswith(prefix):
        return os.path.relpath(abs_path, root)
    return os.path.basename(path_str)


def reformat_and_split(input_csv: str, root_dir: str, output_base: str):
    df = pd.read_csv(input_csv)

    # Check if any protein_path or ligand_path starts with the root_dir
    root_abs = os.path.abspath(root_dir) + os.sep
    all_paths = pd.concat([df['protein_path'], df['ligand_path']]).astype(str)
    if not any(os.path.abspath(p).startswith(root_abs) for p in all_paths):
        print(f"Error: None of the paths in the CSV start with the provided root directory: {root_dir}")
        exit(1)

    for split_name in ('train', 'validation'):
        subset = df[df['split'] == split_name]
        if subset.empty:
            continue

        df_new = pd.DataFrame({
            'key':     subset['system_id'],
            'pk':      subset['pK'],
            'protein': subset['protein_path'].map(lambda p: strip_prefix(p, root_dir)),
            'ligand':  subset['ligand_path'].map(lambda p: strip_prefix(p, root_dir)),
        })

        out_path = f"{output_base}_{split_name}.csv"
        df_new.to_csv(out_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reformat CSV, strip prefix, and split into train/validation files'
    )
    parser.add_argument('input_csv',  help='Original CSV file path')
    parser.add_argument('root_dir',   help='Root directory to strip from absolute paths')
    parser.add_argument('output_base',help='Base name for output files (without _train/_validation suffix)')
    args = parser.parse_args()

    reformat_and_split(args.input_csv, args.root_dir, args.output_base)
