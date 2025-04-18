# Delta Generator
A cli tool for creating and applying deltas between files.  
Let's say you have a 2M word file. You want to have a history, so you're saving versions. But, why should every version be 2M as well? Most content stays the same. So, similar to git but more advanced, this tool allows you to take 2 files and create a small delta file between them. The delta file can then be applied on each one of the files, to create the other.

## Usage
To install the package:
```bash
python setup.py build_ext --inplace
```

To use the commands:
```bash
delta-gen -h # Generating a delta file
delta-apply -h # Applying a delta file
```

Hope you enjoy!