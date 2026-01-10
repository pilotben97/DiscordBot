import csv
import os
from datetime import datetime
from typing import List, Optional
from Classes.Aircraft import Aircraft
from HelperFiles.misc_helper import is_valid_hex


def process_uscg_aircraft_csv(file_path: str):
    aircraft_list = []
    header = None
    data_start_index = None
    key_col_index = None

    # Read and parse the CSV
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

        #for row in rows[:5]:
        #    print(row)

        # Find header row where a column starts with 'hex'
        for i, row in enumerate(rows):
            if any(cell.lower().startswith("hex") for cell in row):
                header = row
                data_start_index = i + 1
                break

        if not header:
            raise ValueError("No header row with 'HEX' found.")
        #print(f"Ehhhhh{header}")

        # Determine which columns to include (stop before "Key")
        try:
            key_col_index = next(i for i, col in enumerate(header) if "key" in col.lower())
        except StopIteration:
            key_col_index = len(header)

        header = header[:key_col_index]

        # Process rows into Aircraft objects
        for row in rows[data_start_index:]:
            if len(row) < key_col_index:
                continue
            
            #print(row)

            record = dict(zip(header, row[:key_col_index]))
            #print(record)

            hex_code = next((value for key, value in record.items() if key.lower().startswith("hex") and value.strip()), None)

            if not hex_code or not is_valid_hex(hex_code):
                continue
            
            
            newicao = fixicao(record.get("Aircraft Type"))

            aircraft = Aircraft(
                hexCode=hex_code,
                icao=newicao,
                callsign=f"C{record.get('CG#').strip()}" if record.get("CG#") and record.get("CG#").strip() else None,
                callsignAbbr=f"C{record.get('CG#').strip()}" if record.get("CG#") and record.get("CG#").strip() else None,
                tailNumber=f"C{record.get('CG#').strip()}" if record.get("CG#") and record.get("CG#").strip() else None,
                operator="US Coast Guard",
                lastAirport=record.get("Last Airport").strip() if record.get("Last Airport") and record.get("Last Airport").strip() else "ZZZZ",
                lastDistance=record.get("Last Distance").strip() if record.get("Last Distance") and record.get("Last Distance").strip() else "0",
                lastLat=record.get("Last Lat").strip() if record.get("Last Lat") and record.get("Last Lat").strip() else "0.0",
                lastLon=record.get("Last Lon").strip() if record.get("Last Lon") and record.get("Last Lon").strip() else "0.0",
                base=record.get("Base").strip() if record.get("Base") and record.get("Base").strip() else "ZZZZ",
                companyCode=int(record.get("Company Code")) if record.get("Company Code") and record.get("Company Code").strip().isdigit() else 0000,
                source=record.get("Source"),
                notes=record.get("Notes")
            )
            aircraft_list.append(aircraft)

        if not aircraft_list:
            print("⚠️ No valid aircraft found. Exiting without export.")
            return
            
    #for row in aircraft_list[:5]:
    #       print(row)
    

    # Export to CSV
    os.makedirs("Data", exist_ok=True)
    export_path = os.path.join("Data", "export.csv")
    with open(export_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=aircraft_list[0].to_dict().keys())
        writer.writeheader()
        for aircraft in aircraft_list:
            writer.writerow(aircraft.to_dict())

    # print(f"✅ Exported {len(aircraft_list)} aircraft to {export_path}")
    
    return aircraft_list

def fixicao(ac_type):
    if "H-65" in ac_type:
        return "AS65"
    if "HC-144" in ac_type:
        return "CN35"
    if "HC-130J" in ac_type:
        return "C30J"
    if "HC-130H" in ac_type:
        return "C130"
    if "H-60" in ac_type:
        return "H60"
    if "HC-27J" in ac_type:
        return "C27"
    if "C-37" in ac_type:
        return "GLF5"
    else:
        return ac_type