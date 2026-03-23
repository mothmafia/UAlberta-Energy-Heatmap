import pandas as pd
import folium
from folium.plugins import HeatMap

# loading data from form
CSV_URL = ( 
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQZAMnUVOgFZdIgt4Zw7hr18bk2Oxwm2pjLzsqaqK15-U48f9YMtXoFQJF64E7seY_wCJ5YRPuMR5mE"
    "/pub?gid=1785731843&single=true&output=csv"
    )
df = pd.read_csv(CSV_URL)
print("data loaded:", df.shape)