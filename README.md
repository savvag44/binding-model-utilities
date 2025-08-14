# Data Processing Tools

This directory contains a collection of Python scripts for processing molecular binding data, converting file formats, and calculating performance metrics for machine learning models.

### 1. `pdb_generator.py`

Converts a dataset containing .sdf ligand files into one containing .pdb files, while preserving protein .pdb files.

**Usage**:
```bash
python3 pdb_generator.py <input_root> <csv_file> <output_root>
```

**Arguments**:
- `input_root`: Original root dataset directory
- `csv_file`: CSV file with protein and ligand file paths relative to root directory (columns: protein, ligand)
- `output_root`: Output directory for converted PDB files

**Example**:
```bash
python3 pdb_generator.py /home/user/data/FEP /home/user/data/FEP_reformat.csv /home/user/data/FEP_pdb
```

**Requirements**: OpenBabel

### 2. `reformatter.py`

Reformats CSV files formatted for [AEV-PLIG](https://github.com/weitse-hsu/AEV-PLIG-refined/) (e.g. ./FEP_benchmark.csv) into the format used by [ToolboxSF](https://github.com/guydurant/toolboxsf) (e.g. ./FEP_reformat.csv)

**Usage**:
```bash
python3 reformatter.py <input_csv> <root_dir> <output_csv>
```

**Arguments**:
- `input_csv`: Original CSV file with columns system_id, pK, protein_path, ligand_path
- `root_dir`: Root directory to strip from absolute paths
- `output_csv`: Output CSV

**Example**:
```bash
python3 reformatter.py FEP_benchmark.csv /home/user/data/FEP FEP_reformat.csv
```

**Output Format**:
- `key`: System identifier
- `pk`: pK value (binding affinity)
- `protein`: path to protein file (relative to a root directory)
- `ligand`: path to ligand file (relative to a root directory)

### 3. `reformat_train_valid_split.py`

Similar to reformatter.py but splits the dataset into separate training and validation CSV files based on the 'split' column, as found in AEV-plig .csv files.

**Usage**:
```bash
python3 reformat_train_valid_split.py <input_csv> <root_dir> <output_base>
```

**Arguments**:
- `input_csv`: CSV file with 'split' column (values: 'train', 'validation')
- `root_dir`: Root directory for path stripping
- `output_base`: Base name for output files

**Example**:
```bash
python3 reformat_train_valid_split.py dataset.csv /data/root/ my_dataset
# Creates: my_dataset_train.csv, my_dataset_validation.csv
```

### 4. `metrics.py`

Calculates performance metrics for machine learning model predictions with bootstrap uncertainty estimation.
Can also perform weighted bootstrapping based on protein groups, as implemented in [AEV-PLIG](https://github.com/weitse-hsu/AEV-PLIG-refined/).

**Usage**:
```bash
python3 metrics.py <csv_file> [-g group_lookup_file] [--n_iterations N] [--n_min MIN]
```

**Arguments**:
- `csv_file`: CSV with columns key, pred, pk (predictions and true values)
- `-g, --group_lookup`: Optional CSV for grouped metrics (system_id → group_id mapping)
- `--n_iterations`: Bootstrap iterations (default: 500)
- `--n_min`: Minimum group size for grouped metrics (default: 10)

**Example**:
```bash
# Basic metrics
python3 metrics.py predictions.csv

# Weighted metrics by protein family
python3 metrics.py predictions.csv -g FEP_benchmark.csv
```

The results .csv file would look like:
```csv
key,pred,pk
id1,8.2,8.5
```

The group id lookup .csv file must contain the following (the AEV-plig formatted .csv files will work)
```csv
system_id,group_id
id1,protein_family_1
```


### 5. `metric_ensembles.py`

Similar to metrics.py, but calculates metrics for multiple models, then forms an "ensemble model" by taking the average prediction of the individual models for each complex.

**Usage**:
```bash
python3 metric_ensembles.py <base_dir> [-e ensemble_file] [-o output_file] [-g group_lookup] [options]
```

**Arguments**:
- `base_dir`: Directory containing model{n} subdirectories
- `-e, --ensemble_file`: Output ensemble CSV file (default: base_dir/ensemble.csv)
- `-o, --output_file`: Output metrics log file (auto-named based on weighting)
- `-g, --group_lookup`: CSV for weighted metrics
- `--n_iterations`: Bootstrap iterations (default: 500)
- `--n_min`: Minimum group size (default: 10)

**Expected Directory Structure**:
```
base_dir/
├── model1/
│   └── data/
│       └── results/
│           └── predictions.csv
├── model2/
│   └── data/
│       └── results/
│           └── predictions.csv
└── ...
```

If your directory structure is different you will need to modify the script a bit, should be easy to do :)

**Example**:
```bash
python3 metric_ensembles.py /path/to/models -g FEP_benchmark.csv
# Creates weighted ensemble metrics and saves to metrics_weighted.log
```

### 6. `calc_metrics.py`

Core library providing the `MetricCalculator` class and utility functions used by other scripts. Contains implementation of all statistical metrics with bootstrap uncertainty estimation.

### 7. Data Files

- **`FEP_benchmark.csv`**: FEP benchmark testset in the AEV-plig format
- **`FEP_reformat.csv`**: FEP benchmark reformatted with reformatter.py

### Python Packages
```bash
pip install pandas numpy scipy rdkit-pypi tqdm numba openbabel
```



