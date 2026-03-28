import pandas as pd
import requests
import time
from rapidfuzz import process
import json

# load geocache
with open("geocache.json", "r") as f:
    geocache = json.load(f)

# loading data from form
CSV_URL = ( 
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQZAMnUVOgFZdIgt4Zw7hr18bk2Oxwm2pjLzsqaqK15-U48f9YMtXoFQJF64E7seY_wCJ5YRPuMR5mE"
    "/pub?gid=1785731843&single=true&output=csv"
    )
df = pd.read_csv(CSV_URL)
print("data loaded:", df.shape)

# handle Other building responses with Nominatim for coords
def geocode_building(name):
    # check cache
    if name in geocache:
        if geocache[name] is None:
            print(f"skip cached unresolvable: '{name}'")
            return None
        print(f"cached '{name}'")
        return tuple(geocache[name])
    
    # call Nominatim, if not cached
    query = f"{name} University of Alberta Edmonton"
    time.sleep(1)
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "json", "limit": 1},
        headers={"User-Agent": "campus-heatmap"}
    )
    results = response.json()
    if results:
        lat = float(results[0]["lat"])
        lng = float(results[0]["lon"])
        print(f"geocoded '{name}' to ({lat}, {lng})")
        geocache[name] = [lat, lng]
        coords = (lat, lng)
    else:
        print(f"could not geocode: '{name}'")
        geocache[name] = None
        coords = None
    
    # save updated cache
    with open("geocache.json", "w") as f:
        json.dump(geocache, f, indent=4)

    return coords

# building coords
BUILDING_COORDS = {
    "CAB": (53.52676645448945, -113.52480769156128),
    "CCIS": (53.528984914149206, -113.524919471152),
    "ETLC": (53.527214309174376, -113.52895865951258),
    "CSC": (53.526834965644575, -113.52712642882692),
    "Cameron Library": (53.526840443360776, -113.523609271156),
    "Rutherford Library": (53.5260066123608, -113.52161971532878),
    "SUB": (53.52543555798063, -113.52741125766217),
    "ECHA": (53.52116705153968, -113.52643514131711),
    "Business": (53.52751234063427, -113.52187859997862),
    "Tory": (53.52791599518946, -113.52198425766233),
    "FAB": (53.524453, -113.520023),
    "Old Arts": (53.526759, -113.52243),
    "MEC": (53.527809, -113.527898),
    "UCOMM": (53.52566309344302, -113.52333876447742),
    "Sperber": (53.52223941490952, -113.52654564888937),
    "BioSci": (53.52914050410567, -113.52559957300794),
    "HUB Mall": (53.52629867966295, -113.5206656210059),
}

BUILDING_ALIASES = {
    "MEC": ["mech e", "mec e"],
    "HUB Mall": ["painting studios", "below hub", "hub basement", "hub", "there is a painting studio"],
    "UCOMM": ["ucom", "ucommons", "university commons"],
}

ALIASES = {alias: building for building, aliases in BUILDING_ALIASES.items() for alias in aliases}

# parse responses
BUILDING_COL = "Which building(s) do you usually crash in?"
def match_building(b):
    b_lower = b.lower()

    # exact match
    match = next((k for k in BUILDING_COORDS if k.lower() == b_lower), None)

    # alias match
    if not match:
        match = next((ALIASES[a] for a in ALIASES if a in b_lower), None)
        if match:
            print(f"alias matched '{b}' to '{match}'")
            
    # fuzzy match
    if not match:
        result = process.extractOne(b, BUILDING_COORDS.keys())
        if result and result[1] >= 80:
            match = result[0]
            print(f"fuzzy matched '{b}' to '{match}' ({result[1]:.0f}%)")
    
    # geocode
    if not match:
        coords = geocode_building(b)
        if coords:
            BUILDING_COORDS[b] = coords
            match = b

    return match

building_rows = []
for _, row in df.iterrows():
    cell = row[BUILDING_COL]
    if pd.notna(cell):
        for b in str(cell).split(","):
            match = match_building(b.strip())
            if match:
                building_rows.append(match)

# intensity / weight on the heatmap
counts = pd.Series(building_rows).value_counts()
print("counts:\n", counts)