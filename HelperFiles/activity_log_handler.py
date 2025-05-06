import os
import csv
import pandas as pd
from datetime import datetime, timedelta
import shutil
from Classes.Aircraft import Aircraft
from Classes.ADSBData import ADSBData


log_path_aircraft = "activity_log_aircraft.csv"
log_path_adsb = "activity_log_adsb.csv"

async def log_activity(moving):
    base_dir = "Data"
    backup_dir = os.path.join(base_dir, "backups")
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)

    aircraft_path = os.path.join(base_dir, "activity_log_aircraft.csv")
    adsb_path = os.path.join(base_dir, "activity_log_adsb.csv")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Backup existing files
    for path, label in [(aircraft_path, "aircraft"), (adsb_path, "adsb")]:
        if os.path.exists(path):
            shutil.copy(path, os.path.join(backup_dir, f"activity_log_{label}_{timestamp}.csv"))

    # Remove old backups
    for fname in os.listdir(backup_dir):
        fpath = os.path.join(backup_dir, fname)
        if os.path.isfile(fpath):
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            if datetime.now() - mtime > timedelta(days=14):
                os.remove(fpath)

    def load_existing(path, key_field):
        data = {}
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = row.get(key_field, "").upper()
                    if key:
                        data[key] = row
        return data

    # Load existing data
    existing_aircraft = load_existing(aircraft_path, "hexCode")
    existing_adsb = load_existing(adsb_path, "hex")

    # Update existing with new records
    for aircraft_obj, adsb_obj in moving:
        aircraft_dict = aircraft_obj.to_dict()
        adsb_dict = adsb_obj.to_dict()

        hexcode = aircraft_dict.get("hexCode", "").upper()
        if hexcode:
            existing_aircraft[hexcode] = aircraft_dict
        hexcode_adsb = adsb_dict.get("hex", "").upper()
        if hexcode_adsb:
            existing_adsb[hexcode_adsb] = adsb_dict

    # Sort aircraft by lastSeenDate descending
    def parse_date(row):
        val = row.get("lastSeenDate")
        try:
            return datetime.fromisoformat(val) if val else datetime.min
        except Exception:
            return datetime.min

    sorted_aircraft = sorted(existing_aircraft.values(), key=parse_date, reverse=True)

    # Collect final fieldnames
    aircraft_fields = sorted({k for row in sorted_aircraft for k in row.keys()})
    adsb_fields = sorted({k for row in existing_adsb.values() for k in row.keys()})

    # Write aircraft log
    with open(aircraft_path, "w", newline='', encoding='utf-8') as fa:
        writer = csv.DictWriter(fa, fieldnames=aircraft_fields)
        writer.writeheader()
        writer.writerows(sorted_aircraft)

    # Write adsb log
    with open(adsb_path, "w", newline='', encoding='utf-8') as fb:
        writer = csv.DictWriter(fb, fieldnames=adsb_fields)
        writer.writeheader()
        writer.writerows(existing_adsb.values())


def load_aircraft_adsb_from_activity():
    aircraft_df = pd.read_csv(f"Data/{log_path_aircraft}")
    adsb_df = pd.read_csv(f"Data/{log_path_adsb}")

    aircraft_map = {}

    # Build aircraft map by hexCode
    for _, row in aircraft_df.iterrows():
        try:
            last_seen = pd.to_datetime(row.get("lastSeenDate")) if pd.notnull(row.get("lastSeenDate")) else None
        except Exception:
            last_seen = None

        # Parse lastAirports if stringified list
        last_airports = row.get("lastAirports")
        if isinstance(last_airports, str) and last_airports.startswith("["):
            try:
                last_airports = ast.literal_eval(last_airports)
            except Exception:
                last_airports = []
        elif pd.isna(last_airports):
            last_airports = []
        else:
            last_airports = [last_airports]

        aircraft = Aircraft(
            hexCode=row.get("hexCode") or row.get("hex"),
            icao=row.get("icao"),
            callsign=row.get("callsign"),
            callsignAbbr=row.get("callsignAbbr"),
            tailNumber=row.get("tailNumber"),
            operator=row.get("operator"),
            lastAirport=row.get("lastAirport"),
            lastDistance=str(row.get("lastDistance")) if pd.notnull(row.get("lastDistance")) else None,
            lastLat=str(row.get("lastLat")) if pd.notnull(row.get("lastLat")) else None,
            lastLon=str(row.get("lastLon")) if pd.notnull(row.get("lastLon")) else None,
            base=row.get("base"),
            companyCode=int(row.get("companyCode")) if pd.notnull(row.get("companyCode")) else None,
            lastSeenDate=last_seen,
            source=row.get("source"),
            notes=row.get("notes"),
            lastAirports=last_airports
        )

        aircraft_map[aircraft.hexCode] = aircraft

    # Combine with ADSB data
    result = []
    for _, row in adsb_df.iterrows():
        hexcode = row.get("hex", "").upper()
        adsb_data = ADSBData(**row.to_dict())
        aircraft = aircraft_map.get(hexcode)
        if aircraft:
            result.append((aircraft, adsb_data))

    return result