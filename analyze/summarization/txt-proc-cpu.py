import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

# INPUT_FILE_PATH = Path("proc-cpu-data.txt")
# OUTPUT_CSV_FILE = Path("proc_cpu_summary.csv")
# VERBOSE_LOGGING = False

def process_program_cpu_usage(file_path: Path, verbose: bool = False):

    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None

    # print(f"Processing program CPU usage file: {file_path}...")

    extracted_records = []
    line_num = 0
    parsing_errors = 0
    processed_lines = 0

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    data_entry = json.loads(line)
                    timestamp = data_entry.get("TimeStamp")
                    name = data_entry.get("Name")
                    cpu_percent = data_entry.get("Cpu")

                    if timestamp is None or name is None or cpu_percent is None:
                        if verbose: print(f"Warning: Skipping line {line_num}. Missing TimeStamp, Name, or Cpu.")
                        continue

                    extracted_records.append({
                        'TimeStamp': int(timestamp),
                        'Name': name,
                        'CpuPercent': float(cpu_percent)
                    })
                    processed_lines += 1

                except Exception as e:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to error: {e}")
                    continue

    except Exception as e:
        print(f"An error occurred during file reading: {e} for file: {file_path}")
        return None

    if not extracted_records:
        print("No valid process CPU records extracted. for file: {file_path}")
        return None

    df = pd.DataFrame(extracted_records)
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], unit='s', errors='coerce')
    df['CpuPercent'] = pd.to_numeric(df['CpuPercent'], errors='coerce')
    df.dropna(subset=['TimeStamp', 'Name', 'CpuPercent'], inplace=True)

    if df.empty:
        print("DataFrame is empty after initial processing and cleaning for file: {file_path}.")
        return None

    # --- Calculate Total Observation Duration ---
    distinct_timestamps = df['TimeStamp'].sort_values().unique()

    if len(distinct_timestamps) < 2:
         print("Warning: Need at least two distinct measurement timestamps to calculate time-weighted average for file: {file_path}.")
         summary = df.groupby('Name')['CpuPercent'].agg(MaxCpuUsage='max').reset_index()
         summary['TimeWeightedAvgCpuPercent'] = np.nan
         return summary[['Name', 'TimeWeightedAvgCpuPercent', 'MaxCpuUsage']]
    else:
         min_ts = pd.to_datetime(distinct_timestamps.min())
         max_ts = pd.to_datetime(distinct_timestamps.max()) # Last timestamp where *any* measurement occurred

    total_duration_seconds = (max_ts - min_ts).total_seconds()
    # print(f"Total observation time span: {total_duration_seconds:.2f} seconds (from {min_ts} to {max_ts})")

    if total_duration_seconds <= 0:
        print("Warning: Total duration is zero or negative. Cannot calculate time-weighted average for file: {file_path}")
        summary = df.groupby('Name')['CpuPercent'].agg(MaxCpuUsage='max').reset_index()
        summary['TimeWeightedAvgCpuPercent'] = np.nan
        return summary[['Name', 'TimeWeightedAvgCpuPercent', 'MaxCpuUsage']]


    ts_map = {pd.Timestamp(t): pd.Timestamp(next_t) for t, next_t in zip(distinct_timestamps[:-1], distinct_timestamps[1:])}
    df['NextOverallTimeStamp'] = df['TimeStamp'].map(ts_map)
    df['Duration'] = (df['NextOverallTimeStamp'] - df['TimeStamp']).dt.total_seconds()
    df.fillna({'Duration': 0}, inplace=True)
    df['Duration'] = df['Duration'].clip(lower=0)


    df['CpuWeighted'] = df['CpuPercent'] * df['Duration']

    if verbose:
        print("\n--- DataFrame with Corrected Durations and Weights Head ---")
        df_sorted = df.sort_values(by=['Name', 'TimeStamp'])
        print(df_sorted[['Name', 'TimeStamp', 'CpuPercent', 'NextOverallTimeStamp', 'Duration', 'CpuWeighted']].head(10))


    # --- Aggregation ---
    summary = df.groupby('Name').agg(
        TotalCpuWeighted=('CpuWeighted', 'sum'),
        MaxCpuUsage=('CpuPercent', 'max'),
        Duration=('Duration', 'sum'),
        DataPoints=('CpuPercent', 'count')
    ).reset_index().sort_values(by='TotalCpuWeighted',ascending=False)

    # Sum(CPU_i * Duration_i) / TotalDuration
    summary['AvgCpuPercent'] = summary['TotalCpuWeighted'] / summary['Duration']

    # print("Calculations complete.")

    summary = summary[[
        'Name','Duration', 'AvgCpuPercent', 'MaxCpuUsage', 'DataPoints'
    ]]

    return summary


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Parse and process the (json-like) data collected from the discern project to display the summary",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument(
        "input_file", 
        type=Path,
        help="Path to the input file change log (proc-cpu-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='proc-cpu-summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary = process_program_cpu_usage(args.input_file, verbose=args.verbose)
    
    # final_summary = process_program_cpu_usage(INPUT_FILE_PATH, verbose=VERBOSE_LOGGING)
    if final_summary is not None and not final_summary.empty:
        
        pd.set_option('display.max_rows', None) # Show all rows
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', '{:.3f}'.format) # Format floats
        final_summary.sort_values(by='AvgCpuPercent', ascending=False)
        # print(final_summary.sort_values(by='AvgCpuPercent', ascending=False))

        # --- Optional: Save to CSV File ---
        if args.output:
            try:
                final_summary.to_csv(args.output, index=False)
                # print(f"\nSummary saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving summary to CSV: {e} for file: {args.input_file}")
    else:
        print("\nNo program CPU usage summary statistics generated.")
