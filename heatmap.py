import pandas as pd
import folium
from folium.plugins import HeatMap
import requests
import time

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
        print(f"geocoded '{name} to ({lat}, {lng})")
        return (lat, lng)
    
    else:
        print(f"could not geocode: '{name}'")
        return None

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
}

BUILDING_COL = "Which building(s) do you usually crash in?"
building_rows = []
for _, row in df.iterrows():
    cell = row[BUILDING_COL]
    if pd.notna(cell):
        for b in str(cell).split(","):
            b = b.strip()
            match = next((k for k in BUILDING_COORDS if k.lower() == b.lower()), None)
            if match:
                building_rows.append(match)
            else:
                coords = geocode_building(b)
                if coords:
                    BUILDING_COORDS[b] = coords
                    building_rows.append(b)

# itensity / weight on the heatmap
counts = pd.Series(building_rows).value_counts()
print("counts:\n", counts)

# create map
m = folium.Map(
    location=[53.52378469455345, -113.52631224576302],
    zoom_start = 16,
    tiles="OpenStreetMap",
)

heat_data = [
    [BUILDING_COORDS[b][0], BUILDING_COORDS[b][1], count]
    for b, count in counts.items()
]

HeatMap(
    heat_data,
    radius = 35,
    blur = 20,
    min_opacity = 0.4,
    gradient = {0.2: "#E6FAFA", 0.5: "#FEE090", 0.8: "#F46d43", 1.0:"#D73027"}
).add_to(m)

# markers with hover tooltips
for building, (lat,lng) in BUILDING_COORDS.items():
    count = counts.get(building, 0)
    folium.CircleMarker(
        location = [lat, lng],
        radius = 6,
        color = "white",
        fill = True,
        fill_color = "#333",
        fill_opacity = 0.8,
        tooltip = f"<b>{building}</b><br>{count} responses",
    ).add_to(m)

m.save("campus_heatmap.html")
print("saved")