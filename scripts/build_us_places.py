"""Build data/us_places.csv from the US Census Gazetteer files.

The fuel price CSV has city + state but no coordinates. This script turns the
Census list of US places (cities, towns, CDPs) and county subdivisions
(townships) into one small lookup file: name, state, lat, lon, kind.

Download (public domain):
  https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_place_national.zip
  https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_cousubs_national.zip

Usage:
  python scripts/build_us_places.py PLACES.txt COUSUBS.txt data/us_places.csv
"""
import csv
import sys


def rows(path, kind):
    with open(path, encoding="latin-1") as f:
        reader = csv.reader(f, delimiter="\t")
        header = [h.strip() for h in next(reader)]
        for raw in reader:
            rec = dict(zip(header, (c.strip() for c in raw)))
            yield rec["NAME"], rec["USPS"], rec["INTPTLAT"], rec["INTPTLONG"], kind


def main(places_path, cousubs_path, out_path):
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "state", "lat", "lon", "kind"])
        count = 0
        for path, kind in ((places_path, "place"), (cousubs_path, "cousub")):
            for row in rows(path, kind):
                writer.writerow(row)
                count += 1
    print(f"Wrote {count} places to {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
