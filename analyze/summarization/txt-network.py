import json
import pandas as pd
import numpy as np
from pathlib import Path
import argparse



# INPUT_FILE_PATH = Path("network-data.txt")
# OUTPUT_CSV_FILE = Path("net-res.csv")
# VERBOSE_LOGGING = False
SORT_BY_COLUMN = 'TotalBytes'

def create_canonical_pair(ip1, ip2):
    """Creates a sorted tuple representing the IP pair."""
    return tuple(sorted((ip1, ip2)))

def process_all_pairs_file(file_path: Path, verbose: bool = False):
    """
    Reads the JSON Lines file, processes all IP packets, calculates network
    statistics per unique communication pair {IP_A, IP_B}, and returns a
    summary DataFrame.
    """
    if not file_path.is_file():
        print(f"Error: Input file not found at {file_path}")
        return None

    # print(f"Processing file: {file_path}")
    # print(f"Analyzing ALL communication pairs...")

    extracted_packets = []
    line_num = 0
    parsing_errors = 0
    processed_lines = 0
    packets_processed = 0
    packets_skipped_no_ip = 0

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line_num += 1
                try:
                    data_batch = json.loads(line)
                    packets = data_batch.get("Packets", [])

                    if not packets:
                        continue

                    processed_lines += 1
                    for packet in packets:
                        packet_ts = packet.get("TimeStamp")
                        packet_len = packet.get("Length")
                        ip_data = packet.get("IP")

                        if packet_ts is None or packet_len is None or not ip_data:
                            packets_skipped_no_ip += 1
                            continue

                        src_ip = ip_data.get("SRCIP")
                        dst_ip = ip_data.get("DSTIP")

                        if not src_ip or not dst_ip:
                            packets_skipped_no_ip += 1
                            continue

                        ip_pair = create_canonical_pair(src_ip, dst_ip)

                        extracted_packets.append({
                            'PacketTimestamp': int(packet_ts),
                            'Length': int(packet_len),
                            'IP_A': ip_pair[0],
                            'IP_B': ip_pair[1]
                        })
                        packets_processed += 1

                except json.JSONDecodeError:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to JSON decode error.")
                    continue
                except Exception as e:
                    parsing_errors += 1
                    if verbose: print(f"Warning: Skipping line {line_num} due to other error: {e}")
                    continue

    except FileNotFoundError:
        print(f"Error: Input file not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred during file reading: {e} for file: {file_path}.")
        return None

    if parsing_errors > 0: print(f" Lines skipped (parsing error): {parsing_errors} for file: {file_path}")

    if not extracted_packets:
        print("No valid IP packet data for analysis was extracted for file: {file_path}.")
        return None


    # print("Converting extracted data to DataFrame...")
    df = pd.DataFrame(extracted_packets)
    df['PacketTimestamp'] = pd.to_datetime(df['PacketTimestamp'], unit='s', errors='coerce')
    df['Length'] = pd.to_numeric(df['Length'], errors='coerce').fillna(0)
    df.dropna(subset=['PacketTimestamp', 'IP_A', 'IP_B'], inplace=True)

    if df.empty:
        print("DataFrame is empty after initial processing and cleaning for file: {file_path}.")
        return None

    # print(f"DataFrame created with {len(df)} relevant packet entries.")
    if verbose:
        print("\n--- Processed DataFrame Head ---")
        print(df.head())

    # print("\nCalculating statistics per communication pair...")
    pair_grouping_keys = ['IP_A', 'IP_B']

    bytes_per_second = df.groupby(
        pair_grouping_keys + [pd.Grouper(key='PacketTimestamp', freq='1s')]
    )['Length'].sum().reset_index()
    bytes_per_second.rename(columns={'Length': 'BytesInSecond'}, inplace=True)

    if bytes_per_second.empty:
        print("Warning: No data after grouping by second for file: {file_path}.")
    elif verbose: print("Per-second byte aggregation complete.")
    peak_bytes = bytes_per_second.groupby(pair_grouping_keys)['BytesInSecond'].max().reset_index()
    peak_bytes['PeakRateMbps'] = peak_bytes['BytesInSecond'] * 8.0 / 1_000_000.0
    if verbose: print("Peak rate calculation complete.")


    avg_rate_data = bytes_per_second.groupby(pair_grouping_keys).agg(
        TotalBytes=('BytesInSecond', 'sum'),
        TotalActiveSeconds=('BytesInSecond', 'count')
    ).reset_index()
    avg_rate_data['AvgRateMbps'] = avg_rate_data.apply(
        lambda row: (row['TotalBytes'] * 8.0 / (row['TotalActiveSeconds'] * 1_000_000.0))
                    if row['TotalActiveSeconds'] > 0 else 0.0, axis=1)
    if verbose: print("Average rate, Total Bytes, Active Seconds calculation complete.")

    total_packets = df.groupby(pair_grouping_keys).size().reset_index(name='TotalPackets')
    if verbose: print("Total packet count complete.")

    if verbose: print("Merging results...")
    summary_df = total_packets
    summary_df = pd.merge(summary_df, avg_rate_data[['IP_A', 'IP_B', 'AvgRateMbps', 'TotalBytes', 'TotalActiveSeconds']], on=pair_grouping_keys, how='left')
    summary_df = pd.merge(summary_df, peak_bytes[['IP_A', 'IP_B', 'PeakRateMbps']], on=pair_grouping_keys, how='left')
    summary_df.fillna(0, inplace=True)

    for col in ['TotalPackets', 'TotalBytes', 'TotalActiveSeconds']:
        if col in summary_df.columns:
             summary_df[col] = summary_df[col].astype(np.int64)
    if verbose: print("Merging complete.")

    summary_df = summary_df[[
        'IP_A', 'IP_B', 'TotalPackets', 'TotalBytes',
        'TotalActiveSeconds', 'AvgRateMbps', 'PeakRateMbps'
    ]]

    return summary_df

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Parse and process the (json-like) data collected from the discern project to display the summary",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument(
        "input_file", 
        type=Path,
        help="Path to the input file change log (network-data.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default='network-summary.csv',
        help="Path to save the output summary CSV file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output during processing."
    )

    args = parser.parse_args()

    final_summary = process_all_pairs_file(args.input_file, verbose=args.verbose)
    # final_summary = process_all_pairs_file(INPUT_FILE_PATH, verbose=VERBOSE_LOGGING)

    if final_summary is not None and not final_summary.empty:
        # print("\n--- Summary Per Communication Pair {IP_A, IP_B} ---")
        pd.set_option('display.max_rows', 200)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1200)
        pd.set_option('display.float_format', '{:.3f}'.format)

        # print(f"Sorting results by '{SORT_BY_COLUMN}' (descending)...")
        final_summary_sorted = final_summary.sort_values(by=SORT_BY_COLUMN, ascending=False)
        # print(final_summary_sorted)

        if args.output:
            try:
                final_summary_sorted.to_csv(args.output, index=False)
                # print(f"\nSummary saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving summary to CSV: {e} for file: {args.input_file}")
    else:
        print("\nNo communication summary statistics generated.")