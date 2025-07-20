import csv
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup


# URL of the page to scrape
URL = "https://elofootball.com/country.php?countryiso=CZE"

TEAM_CODES = {
    "Slavia Praha": "SKS",
    "Viktoria Plzen": "PLZ",
    "AC Sparta Praha": "ACS",
    "Baník Ostrava": "FCB",
    "FK Jablonec": "FKJ",
    "FC Hradec Králové": "HKR",
    "Slovan Liberec": "LIB",
    "Sigma Olomouc": "SIG",
    "FK Teplice": "TEP",
    "FK Mladá Boleslav": "MBL",
    "Bohemians Praha 1905": "BOH",
    "MFK Karviná": "KAR",
    "1. FC Slovácko": "FCS",
    "FK Dukla Praha": "DUK",
    "FK Pardubice": "PCE",
    "FC Zlín": "FCZ"
}

CZECH_NAMES = {
    "Slavia Praha": "Slavia Praha",
    "Viktoria Plzen": "Viktoria Plzeň",
    "AC Sparta Praha": "Sparta Praha",
    "Baník Ostrava": "Baník Ostrava",
    "FK Jablonec": "Jablonec",
    "FC Hradec Králové": "Hradec Králové",
    "Slovan Liberec": "Slovan Liberec",
    "Sigma Olomouc": "Sigma Olomouc",
    "FK Teplice": "Teplice",
    "FK Mladá Boleslav": "Mladá Boleslav",
    "Bohemians Praha 1905": "Bohemians 1905",
    "MFK Karviná": "Karviná",
    "1. FC Slovácko": "Slovácko",
    "FK Dukla Praha": "Dukla Praha",
    "FK Pardubice": "Pardubice",
    "FC Zlín": "Zlín"
}

OUTPUT_CSV = "elo.csv"

def fetch_elo_table():
    """Fetch the ELO table from the web page and return as a list of dicts."""
    resp = requests.get(URL, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("div", id="Ranking").find("table")
    rows = table.find_all("tr")
    elo_data = []
    for row in rows[1:]:  # skip header
        cells = row.find_all(["td", "th"])
        if len(cells) < 9:
            continue  # skip incomplete rows
        team_name = cells[1].get_text(strip=True)
        rating = cells[8].get_text(strip=True)
        short_code = TEAM_CODES.get(team_name)
        if short_code:
            czech_name = CZECH_NAMES.get(team_name)
            elo_data.append({
                "Tým": czech_name,
                "Zkratka": short_code,
                "Elo_rating": rating
            })
    elo_data.sort(key=lambda x: x["Zkratka"])
    return elo_data

def read_existing_csv(filename):
    """Read existing CSV and return as list of dicts."""
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        filtered = (row for row in f if not row.lstrip().startswith("#"))
        reader = csv.DictReader(filtered)
        return list(reader)

def elo_data_changed(new_data, old_data):
    """Check if elo data has changed."""
    return new_data != old_data

def save_to_csv(data, filename):
    """Save elo data to CSV, with timestamp as first comment line."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        # Zapiš timestamp
        now = datetime.now()
        f.write(f"#{now}\n")
        writer = csv.DictWriter(f, fieldnames=["Tým", "Zkratka", "Elo_rating"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main():
    elo_data = fetch_elo_table()
    old_data = read_existing_csv(OUTPUT_CSV)
    if elo_data_changed(elo_data, old_data):
        save_to_csv(elo_data, OUTPUT_CSV)
        print(f"Updated {OUTPUT_CSV} with {len(elo_data)} teams.")
    else:
        print("No change in ELO ratings detected.")

if __name__ == "__main__":
    main()
