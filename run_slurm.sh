#!/bin/bash
#SBATCH --job-name=rich_test_job            # Job name
#SBATCH --output=rich_test_output_%j.txt    # Standard output and error log
#SBATCH --partition=your_partition_name     # Replace with the appropriate partition name
#SBATCH --nodes=1                           # Number of nodes
#SBATCH --ntasks=1                          # Number of tasks
#SBATCH --time=00:05:00                     # Time limit hh:mm:ss

# Load the Python module
module load python/3.13.2  # Adjust the version as needed

# Activate the virtual environment
source /mnt/nfs2/gdsc/hh65/rich-test/.venv/bin/activate

# Set environment variable to force Rich to include ANSI codes
export FORCE_COLOR=true

# Run the Python script
python /mnt/nfs2/gdsc/hh65/rich-test/src/rich_test/rich_output.py

# Deactivate the virtual environment
deactivate
