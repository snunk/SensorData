import csv

input_file = 'data/dataset.csv'   # your original CSV file
output_file = 'data/dataset_cleaned.csv'  # file to save cleaned data

# Collect valid rows first
valid_rows = []
row_occurrences = {}  # key: tuple(row values), value: list of original line numbers
with open(input_file, 'r', newline='') as infile:
    reader = csv.reader(infile)
    for line_num, row in enumerate(reader, start=1):
        # Check if all fields are empty after stripping whitespace
        if not all(cell.strip() == '' for cell in row):
            valid_rows.append(row)
            # Treat first row that starts with 'Epoch' as header; don't include in duplicates
            is_header = line_num == 1 and len(row) > 0 and row[0].strip().lower() == 'epoch'
            if is_header:
                continue
            # When detecting repeating rows, ignore the epoch column (index 0)
            key = tuple(cell.strip() for cell in row[1:])
            row_occurrences.setdefault(key, []).append(line_num)

# Write rows manually to control newlines
cleaned_rows = []
duplicates_removed = 0

# Compute counts per key (excluding epoch) from previously built row_occurrences
key_to_count = {key: len(lines) for key, lines in row_occurrences.items()}

for idx, row in enumerate(valid_rows, start=1):
    # Preserve header if present (starts with 'Epoch')
    if idx == 1 and len(row) > 0 and row[0].strip().lower() == 'epoch':
        cleaned_rows.append(row)
        continue
    key = tuple(cell.strip() for cell in row[1:])
    count = key_to_count.get(key, 0)
    if count > 1:
        duplicates_removed += 1
        continue  # drop all occurrences of duplicate groups
    cleaned_rows.append(row)

with open(output_file, 'w', newline='') as outfile:
    for i, row in enumerate(cleaned_rows):
        if i > 0:
            outfile.write('\n')  # Add newline before each row except the first
        writer = csv.writer(outfile, lineterminator='')
        writer.writerow(row)

print("Cleaning complete! Saved as:", output_file)
print(f"Removed {duplicates_removed} duplicate row(s) (epoch ignored in comparison).")

# Identify and report repeating rows of identical values
duplicates = {key: lines for key, lines in row_occurrences.items() if len(lines) > 1}
if duplicates:
    print("Identical row repeats detected:")
    max_rows_to_show = 5
    max_lines_to_show = 5
    shown = 0
    for key, lines in sorted(duplicates.items(), key=lambda kv: len(kv[1]), reverse=True):
        if shown >= max_rows_to_show:
            remaining = len(duplicates) - shown
            if remaining > 0:
                print(f"... and {remaining} more duplicate row pattern(s) not shown")
            break
        count = len(lines)
        line_list = ', '.join(str(n) for n in lines[:max_lines_to_show])
        if len(lines) > max_lines_to_show:
            line_list += f", ... ({count} total)"
        print(f"- Occurs {count} times at line(s): {line_list}")
        print(f"  Row values (excluding epoch): {list(key)}")
        shown += 1
else:
    print("No repeating identical rows found.")