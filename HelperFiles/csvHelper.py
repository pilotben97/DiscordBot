import csv

def process_csv(file_path, callback):
    results = []
    header_row = []
    found_header = False
    key_index = -1
    hex_col_name = None

    # Step 1: Read lines and detect header row
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().split(',')]

        if not found_header and any("hex" in c.lower() for c in cells):
            header_row = cells
            found_header = True
            hex_col_name = next((c for c in cells if "hex" in c.lower()), None)
            key_index = next((i for i, c in enumerate(cells) if c.lower() == "key"), -1)
            data_start_index = i + 1
            break

    if not found_header or not hex_col_name:
        print("❌ No header row found with a 'Hex' column.")
        return

    # Step 2: Parse CSV from that point
    reader = csv.DictReader(lines[data_start_index:], fieldnames=header_row)

    for row in reader:
        hex_val = row.get(hex_col_name, "").strip()
        if hex_val:
            filtered_row = {}
            for i, key in enumerate(header_row):
                if key_index != -1 and i >= key_index:
                    break
                filtered_row[key] = row.get(key, "").strip()
            results.append(filtered_row)

    callback(results)