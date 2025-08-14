import pandas as pd
import os
import argparse

def reformat_csv(input_csv: str, root_dir: str, output_csv: str):
    """
    Read the input CSV, strip the given root directory from any absolute paths in protein_path
    and ligand_path, and write a new CSV with columns: key, pk, protein, ligand.
    python3 reformatter.py input.csv root_dir output.csv
    """
    df = pd.read_csv(input_csv)
    root_dir = os.path.abspath(root_dir)

    # Check if any protein_path or ligand_path starts with the root_dir
    prefix = root_dir + os.sep
    all_paths = pd.concat([df['protein_path'], df['ligand_path']]).astype(str)
    if not any(os.path.abspath(p).startswith(prefix) for p in all_paths):
        print(f"Error: None of the paths in the CSV start with the provided root directory: {root_dir}")
        exit(1)

    def strip_prefix(path_str: str) -> str:
        abs_path = os.path.abspath(path_str)
        # If path is under the root_dir, make it relative; otherwise use basename
        if abs_path.startswith(prefix):
            return os.path.relpath(abs_path, root_dir)
        return os.path.basename(path_str)

    df_new = pd.DataFrame({
        'key':     df['system_id'],
        'pk':      df['pK'],
        'protein': df['protein_path'].map(strip_prefix),
        'ligand':  df['ligand_path'].map(strip_prefix),
    })

    df_new.to_csv(output_csv, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reformat CSV to key/pk/protein/ligand with relative paths'
    )
    parser.add_argument('input_csv',  help='Path to the original CSV file')
    parser.add_argument('root_dir',   help='Root directory to strip from absolute paths')
    parser.add_argument('output_csv', help='Path for the output formatted CSV file')
    args = parser.parse_args()

    reformat_csv(args.input_csv, args.root_dir, args.output_csv)
