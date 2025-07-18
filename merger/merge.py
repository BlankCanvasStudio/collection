import os
import json
import pandas as pd
import itertools

def generate_unified_dev_id(file1_path, file2_path, default_id="unified.dev.id"):
    """
    Reads the first line of two files to parse their DevIDs and merge them.
    """
    dev_id1, dev_id2 = None, None
    try:
        with open(file1_path, 'r') as f:
            dev_id1 = json.loads(f.readline()).get("DevID")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, AttributeError):
        pass
    try:
        with open(file2_path, 'r') as f:
            dev_id2 = json.loads(f.readline()).get("DevID")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, AttributeError):
        pass

    if not dev_id1 or not dev_id2:
        return default_id

    parts1, parts2 = dev_id1.split('.'), dev_id2.split('.')
    new_parts = []
    for i in range(min(len(parts1), len(parts2))):
        if parts1[i] == parts2[i]:
            new_parts.append(parts1[i])
        else:
            new_parts.append(f"{parts1[i]}-{parts2[i]}")
    return ".".join(new_parts)

def finetune_cpu_data(all_data, file1_path, file2_path):
    """
    Takes a list of combined CPU data and applies pandas-based fine-tuning.
    - Merges entries with the same timestamp.
    - Pads and sums CPU core loads.
    - Unifies the DevID.

    Args:
        all_data (list): The list of combined data dictionaries.
        file1_path (str): Path to the first source file (for DevID generation).
        file2_path (str): Path to the second source file (for DevID generation).

    Returns:
        list: The processed list of data dictionaries.
    """
    print("Applying pandas fine-tuning for cpu-load-data.txt...")
    df = pd.DataFrame(all_data)
    unified_dev_id = generate_unified_dev_id(file1_path, file2_path)

    def merge_cpu_group(group):
        loads_list = group['Load'].tolist()
        max_cores = max(len(l) for l in loads_list) if loads_list else 0
        summed_load = [0.0] * max_cores
        for load_array in loads_list:
            for i, value in enumerate(load_array):
                summed_load[i] += value
        return pd.Series({'Load': summed_load, 'DevID': unified_dev_id})

    # Group by the already-adjusted timestamps and apply the merge logic
    processed_df = df.groupby('TimeStamp').apply(merge_cpu_group, include_groups=False).reset_index()
    
    return processed_df.to_dict('records')


def find_earliest_timestamp(filepath):
    """
    Finds the absolute earliest timestamp in a sorted network data file
    by only inspecting the first valid record.
    """
    try:
        with open(filepath, 'r') as f:
            # Find the first non-empty line
            first_line = ""
            for line in f:
                if line.strip():
                    first_line = line
                    break
            
            if not first_line:
                return float('inf')

            data = json.loads(first_line)
            earliest = int(data["TimeStamp"])
            return earliest

    except FileNotFoundError:
        pass
    except (json.JSONDecodeError, KeyError):
        print(f"Warning: Could not parse first line of {filepath} to find earliest timestamp.")
    
    return float('inf')

def process_network_data(file1_path, file2_path,time_offset_file1, time_offset_file2):
    """
    A separate, isolated pipeline for processing network-data.txt to preserve
    the accuracy of nested timestamps.
    """
    print("Running isolated processing for network-data.txt...")
    all_data = []

    min_timestamp = find_earliest_timestamp(file1_path)
    local_min = find_earliest_timestamp(file2_path)
    
    if min_timestamp == float('inf'):
        print(f"Warning: Could not establish a baseline timestamp from {file1_path}. Cannot process network data.")
        return []

    try:
        with open(file1_path, 'r') as f:
            for line in f:
                 if not line.strip(): continue
                 try:
                    data = json.loads(line)
                    data["TimeStamp"] = str(int(data["TimeStamp"]) + time_offset_file1)
                    if "Packets" in data and isinstance(data["Packets"], list):
                            for i, packet in enumerate(data["Packets"]):
                                data["Packets"][i]["TimeStamp"] = str(int(data["Packets"][i]["TimeStamp"]) + time_offset_file1)
                    all_data.append(data)
                 except (json.JSONDecodeError, KeyError):
                    print(f"Warning: Could not process line in {file1_path}: {line.strip()}")
    except FileNotFoundError:
        print(f"Warning: File not found: {file1_path}")

    if local_min == float('inf'):
        print(f"Info: No data to process from {file2_path}")
    else:
        try:
            with open(file2_path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        
                        data["TimeStamp"] = str(int(data["TimeStamp"]) - local_min + min_timestamp + time_offset_file2)
                        
                        if "Packets" in data and isinstance(data["Packets"], list):
                            for i, packet in enumerate(data["Packets"]):
                                data["Packets"][i]["TimeStamp"] = str(int(data["Packets"][i]["TimeStamp"]) - local_min + min_timestamp + time_offset_file2)
                        all_data.append(data)
                    except (json.JSONDecodeError, KeyError):
                        print(f"Warning: Could not process line in {file2_path}: {line.strip()}")
        except FileNotFoundError:
            print(f"Warning: File not found: {file2_path}")
            
    return all_data

def process_file_data(file1_path,file2_path,time_offset_file1, time_offset_file2):
    all_data = []
    min_timestamp = find_earliest_timestamp(file1_path)
    if(min_timestamp == float('inf')):
        min_timestamp = find_earliest_timestamp(file2_path)
    local_min = find_earliest_timestamp(file2_path)
    unified_dev_id = generate_unified_dev_id(file1_path, file2_path)
    try:
        with open(file1_path, 'r') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    
                    if data["TimeStamp"] != str(min_timestamp):
                        data["TimeStamp"] = str(int(data["TimeStamp"]) + time_offset_file1)
                    
                    if "DevID" in data:
                        data["DevID"] = unified_dev_id
                        
                    all_data.append(data)
                except (json.JSONDecodeError, KeyError):
                    print(f"Warning: Could not decode or process line in {file1_path}: {line.strip()}")
    except FileNotFoundError:
        print(f"Warning: File not found, skipping: {file1_path}")


    try:
        with open(file2_path, 'r') as f:
            first_line = f.readline()
            if not first_line.strip():
                local_min = 0 
                f.seek(0)
            else:
                try:
                    local_min = int(json.loads(first_line)["TimeStamp"])
                except (json.JSONDecodeError, KeyError):
                    print(f"Warning: Could not get local_min from first line of {file2_path}. Using 0.")
                    local_min = 0
                    f.seek(0)

            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    if data["TimeStamp"] == str(local_min):
                        # not offseting the initial commit
                        data["TimeStamp"] = str(int(data["TimeStamp"]) - local_min + min_timestamp)
                    else:
                        data["TimeStamp"] = str(int(data["TimeStamp"]) - local_min + min_timestamp + time_offset_file2)
                        if "DevID" in data:
                            data["DevID"] = unified_dev_id
                        all_data.append(data)
                except (json.JSONDecodeError, KeyError):
                    print(f"Warning: Could not decode or process line in {file2_path}: {line.strip()}")
    except FileNotFoundError:
        print(f"Warning: File not found, skipping: {file2_path}")
        
    return all_data

def process_and_combine_data(folder1, folder2, output_folder,time_offset_file1, time_offset_file2):
    """
    Main processing function that merges files using your original timestamp logic
    and then calls fine-tuning functions as needed.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    common_files = sorted([
        "cpu-load-data.txt", "file-data.txt", "network-data.txt",
        "proc-cpu-data.txt", "proc-mem-data.txt", "proc-new-data.txt"
    ])

    for filename in common_files:
        print(f"--- Processing {filename} ---")
        file1_path = os.path.join(folder1, filename)
        file2_path = os.path.join(folder2, filename)
        output_file_path = os.path.join(output_folder, filename)

        all_data = []
        min_timestamp = float('inf')

        # seperated processing for network and file data
        if filename == "network-data.txt":
            all_data = process_network_data(file1_path, file2_path,time_offset_file1, time_offset_file2)
            
        elif filename == "file-data.txt":
            all_data = process_file_data(file1_path,file2_path, time_offset_file1, time_offset_file2)
            
            
        else:
            # bug found: if file1 is skipped, file2 does not obtain the propper min_timestamp
            unified_dev_id = generate_unified_dev_id(file1_path, file2_path)
            try:
                with open(file1_path, 'r') as f:
                    for line in f:
                        if not line.strip(): continue
                        try:
                            data = json.loads(line)
                            if(min_timestamp==float('inf')):
                                min_timestamp = int(data["TimeStamp"])
                            
                            data["TimeStamp"] = str(int(data["TimeStamp"]) + time_offset_file1)
                            if "DevID" in data:
                                data["DevID"] = unified_dev_id
                            all_data.append(data)
                        except (json.JSONDecodeError, KeyError):
                            print(f"Warning: Could not decode or process line in {file1_path}: {line.strip()}")
            except FileNotFoundError:
                print(f"Warning: File not found, skipping: {file1_path}")


            try:
                with open(file2_path, 'r') as f:
                    first_line = f.readline()
                    if(min_timestamp==float('inf')):
                        min_timestamp = int(first_line["TimeStamp"])
                    if not first_line.strip():
                        local_min = 0 
                        f.seek(0)
                    else:
                        try:
                            local_min = int(json.loads(first_line)["TimeStamp"])
                        except (json.JSONDecodeError, KeyError):
                            print(f"Warning: Could not get local_min from first line of {file2_path}. Using 0.")
                            local_min = 0
                            f.seek(0)

                    for line in f:
                        if not line.strip(): continue
                        try:
                            data = json.loads(line)
                            data["TimeStamp"] = str(int(data["TimeStamp"]) - local_min + min_timestamp + time_offset_file2)
                            if "DevID" in data:
                                data["DevID"] = unified_dev_id
                            all_data.append(data)
                        except (json.JSONDecodeError, KeyError):
                            print(f"Warning: Could not decode or process line in {file2_path}: {line.strip()}")
            except FileNotFoundError:
                print(f"Warning: File not found, skipping: {file2_path}")

            if filename == "cpu-load-data.txt" and all_data:
                all_data = finetune_cpu_data(all_data, file1_path, file2_path)
                
            
        
        if not all_data:
            print(f"Warning: No data to write for {filename}.")
            open(output_file_path, 'w').close()
            continue
        
        all_data.sort(key=lambda x: int(x['TimeStamp']))

        with open(output_file_path, 'w') as f:
            for data in all_data:
                f.write(json.dumps(data) + '\n')

        print(f"Successfully processed and combined '{filename}'")
        print("-" * (25 + len(filename)))


# --- Configuration ---
# source_folder1 = '../../DISCERN/data/legitimate/dnsmitm/0/cache-data'
# source_folder2 = '../../DISCERN/data/malicious/upload/0/victim2-data'
# output_folder_path = './../../DISCERN/data/merged/dnsmitm_upload/0/cache_victim2/'
# time_offset_file1 = 0
# time_offset_file2 = 0

# # --- Execution ---
# process_and_combine_data(source_folder1, source_folder2, output_folder_path)
def main():
    """
    Main execution function to find subfolders, generate permutations,
    and process them automatically.
    """
    # --- Configuration ---
    parent_folder1 = '../../DISCERN/data/legitimate/synflood/0/'
    parent_folder2 = '../../DISCERN/data/malicious/internetscanner/0/'
    base_output_folder = '../../DISCERN/data/merged/'
    
    # Optional time offsets
    time_offset_file1 = 0
    time_offset_file2 = 0

    # --- Automatic Path and Folder Generation ---
    try:
        # Extract descriptive names like 'dnsmitm' and 'upload' from the paths
        name1 = os.path.basename(os.path.dirname(os.path.abspath(parent_folder1)))
        name2 = os.path.basename(os.path.dirname(os.path.abspath(parent_folder2)))
        # Extract common directory name, e.g., '0'
        common_dir = os.path.basename(os.path.abspath(parent_folder1))
    except Exception as e:
        print(f"Could not automatically determine names from paths. Using placeholders. Error: {e}")
        name1, name2, common_dir = "group1", "group2", ""

    # Construct the specific output directory, e.g., ../../DISCERN/data/merged/dnsmitm_upload/0/
    specific_output_base = os.path.join(base_output_folder, f"{name1}_{name2}", common_dir)

    try:
        subfolders1 = [d for d in os.listdir(parent_folder1) if os.path.isdir(os.path.join(parent_folder1, d)) and d != "summary"]
        subfolders2 = [d for d in os.listdir(parent_folder2) if os.path.isdir(os.path.join(parent_folder2, d)) and d != "summary"]
    except FileNotFoundError as e:
        print(f"Error: Could not find one of the parent directories. Please check paths. {e}")
        return

    if not subfolders1 or not subfolders2:
        print("Warning: One or both parent directories are empty or do not exist.")
        return

    # Generate all combinations (Cartesian product) of the subfolders
    folder_permutations = list(itertools.product(subfolders1, subfolders2))
    
    print(f"Found {len(subfolders1)} subfolders in {parent_folder1}: {subfolders1}")
    print(f"Found {len(subfolders2)} subfolders in {parent_folder2}: {subfolders2}")
    print(f"Generated {len(folder_permutations)} total combinations to process.\n")

    # --- Execution Loop ---
    for i, (subfolder1, subfolder2) in enumerate(folder_permutations):
        print(f"===== Starting Combination {i+1}/{len(folder_permutations)}: {subfolder1} + {subfolder2} =====")
        
        source_path1 = os.path.join(parent_folder1, subfolder1)
        source_path2 = os.path.join(parent_folder2, subfolder2)
        
        # Construct the final output folder path, e.g., ../../merged/dnsmitm_upload/0/cache_victim2/
        output_path = os.path.join(specific_output_base, f"{subfolder1[:-5]}_{subfolder2[:-5]}")
        
        print(f"  Source 1: {source_path1}")
        print(f"  Source 2: {source_path2}")
        print(f"  Output:   {output_path}\n")

        # Call the main processing function with the generated paths and offsets
        process_and_combine_data(source_path1, source_path2, output_path, time_offset_file1, time_offset_file2)
        
        print(f"===== Finished Combination: {subfolder1} + {subfolder2} =====\n")
if __name__ == "__main__":
    main()
