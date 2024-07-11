import argparse
import re

def parse_log_to_pivoted_csv(file_path):
    # Prepare the data structure
    # Data stored as {run_key: {table: time, 'Total Elapsed': total_time}}
    data = {}

    # Regular expressions for parsing
    run_regex = re.compile(r"run:(\d+), PostgresBulk:(\d+), MysqlBatch:(\d+)")
    migration_regex = re.compile(r"Migration of Table:(\w+) is (\d+\.\d+) seconds")
    total_elapsed_regex = re.compile(r"Total Elapsed by the tuples migration is (\d+\.\d+) seconds")

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        # Check for run, PostgresBulk, and MysqlBatch
        run_match = run_regex.search(line)
        if run_match:
            run_number, postgres_bulk, mysql_batch = run_match.groups()
            run_key = f"{run_number},{postgres_bulk},{mysql_batch}"

            if run_key not in data:
                data[run_key] = {}

        # Check for table migration times
        migration_match = migration_regex.search(line)
        if migration_match:
            table, time = migration_match.groups()
            data[run_key][table] = time

        # Capture total elapsed time
        total_elapsed_match = total_elapsed_regex.search(line)
        if total_elapsed_match:
            total_time = total_elapsed_match.group(1)
            data[run_key]['Total Elapsed'] = total_time

    # Gather all unique table names to create headers, excluding 'Total Elapsed'
    all_tables = set()
    for details in data.values():
        all_tables.update(details.keys())
    all_tables.discard('Total Elapsed')  # Remove 'Total Elapsed' to avoid duplication
    sorted_tables = sorted(all_tables)

    # Create CSV headers
    headers = ['Run Number, Postgres Bulk, Mysql Batch'] + sorted_tables + ['Total Elapsed']
    csv_content = ','.join(headers) + '\n'

    # Populate CSV rows
    for run_key, timings in data.items():
        row = [run_key] + [timings.get(table, '') for table in sorted_tables]
        # Add the total elapsed time at the end
        row.append(timings.get('Total Elapsed', ''))
        csv_content += ','.join(row) + '\n'

    return csv_content

def main():
    parser = argparse.ArgumentParser(description='Convert log files to CSV format with simplified headers.')
    parser.add_argument('file_pairs', nargs='+', help='Pairs of input log file path and output CSV file path.')
    args = parser.parse_args()

    if len(args.file_pairs) % 2 != 0:
        raise ValueError("Please provide pairs of input and output file paths.")

    file_pairs = zip(args.file_pairs[::2], args.file_pairs[1::2])

    for input_path, output_path in file_pairs:
        print(f'Processing file: {input_path}')
        csv_output = parse_log_to_pivoted_csv(input_path)
        with open(output_path, 'w') as f:
            f.write(csv_output)
        print(f'Data from {input_path} has been processed and saved to {output_path}')

if __name__ == '__main__':
    main()
