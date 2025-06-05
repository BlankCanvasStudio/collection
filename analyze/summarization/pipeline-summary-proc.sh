#!/bin/bash

# --- Configuration ---

BASE_DIR="./../../../DISCERN/data/legitimate"  # ".../DISCERN/data/malicious" or ".../DISCERN/data/legitimate", 
                                        # adjust the relative path according to the directory on your computer
SCRIPT_DIR="."     # Directory containing the txt-*.py scripts

# --- checks for paths ---

if [[ ! -d "$BASE_DIR" ]]; then
  echo "Error: Base directory not found at $BASE_DIR"
  exit 1
fi

if [[ ! -d "$SCRIPT_DIR" ]]; then
  echo "Error: Script directory not found at $SCRIPT_DIR"
  exit 1
fi

# --- find input files and loop ---
# Use find to locate files named '*-data.txt' exactly 4 levels deep from BASE_DIR
find "$BASE_DIR" -mindepth 4 -maxdepth 4 -type f -name '*-data.txt' -print0 | while IFS= read -r -d $'\0' input_file_path; do

    # Extract identifier 'x' from input filename 'x-data.txt'
    # x = {cpu-load, file, network, proc-cpu, proc-mem, proc-new}
    input_filename=$(basename "$input_file_path")
    identifier="${input_filename%-data.txt}" # Remove the '-data.txt' suffix

    if [[ -z "$identifier" || "$identifier" == "$input_filename" ]]; then
        echo "   Warning: Could not extract identifier from input filename '$input_filename'. Skipping."
        echo "---"
        continue
    fi

    script_filename="txt-${identifier}.py"
    script_file_path="$SCRIPT_DIR/$script_filename"

    # Check if the corresponding Python script actually exists
    if [[ ! -f "$script_file_path" ]]; then
        if [[ "$script_file_path" != "./txt-logs.py" ]]; then
            echo "   Warning: Corresponding script '$script_file_path' not found. Skipping processing for '$input_filename'."
            echo "---"
        fi
        continue
    fi

    # Extract folder structure (f1, f2, f3) from input path relative to BASE_DIR
    # Example: input_file_path = /some/path/folder1/folder2/folder3/x-data.txt
    #         relative_path = folder1/folder2/folder3/x-data.txt
    relative_path="${input_file_path#$BASE_DIR/}"

    # Use dirname/basename to get folder components
    dir_level3=$(dirname "$relative_path")      # e.g., folder1/folder2/folder3

    if [[ -z "$dir_level3" || "$dir_level3" == "." || ! "$dir_level3" =~ / ]]; then
         echo "   Warning: Could not determine valid parent directory structure for '$input_file_path'. Skipping."
         echo "---"
         continue
    fi

    folder3=$(basename "$dir_level3")          # folder3

    dir_level2=$(dirname "$dir_level3")         # folder1/folder2
    folder2=$(basename "$dir_level2")          # folder2

    dir_level1=$(dirname "$dir_level2")         # folder1
    folder1=$(basename "$dir_level1")          # folder1

    # Add further checks if folder names look valid (e.g., not empty) if needed
    if [[ -z "$folder1" || -z "$folder2" || -z "$folder3" ]]; then
        echo "   Warning: Failed to extract all folder components (f1, f2, f3) for '$input_file_path'. Skipping."
        echo "---"
        continue
    fi

    # Construct the dynamic output directory path including 'summary' and 'folder3' (fff)
    output_dir="$BASE_DIR/$folder1/$folder2/summary/$folder3"

    # Construct the output filename
    output_filename="${identifier}-res.csv" # e.g., x-res.csv
    output_file_path="$output_dir/$output_filename"

    # echo "   Output Dir: '$output_dir'"
    # echo "   Output File: '$output_file_path'"

    # Create the output directory (and any parent directories aka 'summary') if it doesn't exist
    mkdir -p "$output_dir"
    if [[ $? -ne 0 ]]; then
        echo "   Error: Failed to create output directory '$output_dir'. Skipping."
        echo "---"
        continue
    fi

    python3 "$script_file_path" "$input_file_path" -o "$output_file_path"

    exit_status=$?
    if [[ $exit_status -ne 0 ]]; then
        echo "   Warning: Python script '$script_filename' exited with status $exit_status."
    fi
    echo "---"

done

echo "Processing finished."
