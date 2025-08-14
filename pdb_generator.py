#!/usr/bin/env python3
# ./pdb_generator.py /home/mert4902/documents/data/HiQBind /home/mert4902/documents/data/hiqbind_reformat.csv /home/mert4902/documents/data/HiQBind_pdb  
import os
import csv
import shutil
import argparse
from tqdm import tqdm

try:
    from openbabel import pybel
    from openbabel import openbabel as ob
except ImportError:
    raise ImportError("Install OpenBabel Python bindings: pip install openbabel")

# Suppress OpenBabel warnings
ob.obErrorLog.SetOutputLevel(0)

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def copy_protein(src_root, dst_root, protein_path):
    src = os.path.join(src_root, protein_path)
    dst = os.path.join(dst_root, protein_path)
    
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source protein file not found: {src}")
    
    ensure_dir(dst)
    shutil.copy2(src, dst)

def convert_ligand(src_root, dst_root, ligand_path):
    src = os.path.join(src_root, ligand_path)
    pdb_rel = ligand_path.rsplit(".", 1)[0] + ".pdb"
    dst = os.path.join(dst_root, pdb_rel)
    
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source ligand file not found: {src}")
    
    ensure_dir(dst)
    
    try:
        molecules = list(pybel.readfile("sdf", src))
        if not molecules:
            raise ValueError(f"No molecules found in SDF file: {src}")
        
        # Convert the first molecule
        mol = molecules[0]
        
        # Write the molecule - mol.write() returns None on success, not True/False
        mol.write("pdb", dst, overwrite=True)
        
        # Check if the file was actually created
        if not os.path.exists(dst) or os.path.getsize(dst) == 0:
            raise RuntimeError(f"PDB file was not created or is empty")
            
    except Exception as e:
        # Log the specific file that failed but continue processing
        print(f"Warning: Failed to convert ligand {src} to PDB: {str(e)}")
        # Create an empty file to indicate this ligand was processed but failed
        with open(dst + ".failed", "w") as f:
            f.write(f"Conversion failed: {str(e)}\n")
        return False
    
    return True

def main():
    p = argparse.ArgumentParser(
        description="Copy proteins and convert ligands with progress bar"
    )
    p.add_argument("input_root",  help="Root dir of source files")
    p.add_argument("csv_file",    help="Path to dataset.csv")
    p.add_argument("output_root", help="Root dir for output .pdbs")
    args = p.parse_args()

    with open(args.csv_file, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in tqdm(rows, desc="Processing entries", unit="file"):
        try:
            copy_protein(args.input_root, args.output_root, row["protein"])
            ligand_success = convert_ligand(args.input_root, args.output_root, row["ligand"])
            if not ligand_success:
                print(f"Skipped ligand conversion for {row['ligand']}")
        except Exception as e:
            print(f"Error processing row {row}: {str(e)}")
            continue

if __name__ == "__main__":
    main()