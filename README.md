# UAlberta-Energy-Heatmap
A visualized heatmap of campus, mapping where and when students hit an energy crash.


## How it works
Survey responses are collected via Google Forms and pulled live into a Python script.
Building names are parsed, matched, and geocoded automatically.
Response counts per building are visualized as a heatmap overlay on an interactive map of campus.


## Built with
- Python, Pandas, Folium
- Nominatim (geocoding)
- RapidFuzz (fuzzy building name matching)
- Google Forms + Sheets


## Data
53+ UAlberta student responses. Ethics cleared by UAlberta REB under TCPS2 (2022).


## Screenshot
![UAlberta Energy Map](image.png)