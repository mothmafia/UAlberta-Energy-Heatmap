import folium
import pandas as pd
from folium.plugins import HeatMap
from heatmap import counts, BUILDING_COORDS, df

# create map
m = folium.Map(
    tiles="CartoDB positron",
    min_zoom = 13,
    max_zoom = 19,
)

# dynamically fit buildings
lats = [BUILDING_COORDS[b][0] for b in counts.index if b in BUILDING_COORDS]
lngs = [BUILDING_COORDS[b][1] for b in counts.index if b in BUILDING_COORDS]

padding = 0.004
south, north = min(lats) - padding, max(lats) + padding
west, east = min(lngs) - padding, max(lngs) + padding

m.fit_bounds([[south, west], [north, east]])
m.options["maxBounds"] = [[south, west], [north, east]]


# title overlay
title_html = """
<style>
    .title-card {
        position: fixed;
        top: -60px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        background: white;
        padding: 10px 24px 30px 24px;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        font-family: sans-serif;
        text-align: center;
        cursor: pointer;
        animation: welcomeSlide 3s cubic-bezier(0.4, 0, 0.2, 1);
        transition: top 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .title-card:hover {
        top: 0px;
    }
    @keyframes welcomeSlide {
        0% { top: -60px; }
        20% { top: 0px; }
        70% { top: 0px; }
        100% { top: -60px; }
    }
</style>
<div class="title-card">
    <div style="font-size: 16px; font-weight: 600; color: #223823; letter-spacing: 0.3px;">
        UAlberta Energy Map
    </div>
    <div style="font-size: 11px; color: #999; margin-top: 3px;">
        where students crash on campus
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

last_updated = pd.to_datetime(df["Timestamp"]).max().strftime("%b %d, %Y")
# legend overlay
legend_html = f"""
<style>
    .legend-card {{
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
        background: rgba(255,255,255,0.75);
        padding: 8px 12px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-family: sans-serif;
    }}
    .legend-bar {{
        width: 120px;
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(to right, #c9b8f5, #89a4f7, #f4a89a, #f5c842);
    }}
    .legend-labels {{
        display: flex;
        justify-content: space-between;
        font-size: 9px;
        color: #999;
        margin-top: 4px;
    }}
    .legend-count{{
        font-size: 9px;
        color: #bbb;
        margin-top: 5px;
        text-align: center;
    }}
</style>
<div class="legend-card">
    <div class="legend-bar"></div>
    <div class="legend-labels">
        <span>low</span>
        <span>high</span>
    </div>
    <div class="legend-count">{len(df)} students surveyed</div>
    <div class="legend-count">last updated: {last_updated}</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

heat_data = [
    [BUILDING_COORDS[b][0], BUILDING_COORDS[b][1], count]
    for b, count in counts.items()
]

HeatMap(
    heat_data,
    radius = 50,
    blur = 40,
    min_opacity = 0.3,
    gradient = {
        0.0: "#C9B8F5",
        0.3: "#89A4F7",
        0.6: "#F4A89A",
        1.0: "#F5C842",
    },
).add_to(m)

# markers with hover tooltips
for building, (lat,lng) in BUILDING_COORDS.items():
    count = counts.get(building, 0)
    if count > 0:
        folium.CircleMarker(
            location = [lat, lng],
            radius = 6,
            color = "white",
            weight = 2,
            fill = True,
            fill_color = "rgba(255,255,255,0.15)",
            fill_opacity = 1,
            tooltip = folium.Tooltip(
                f"<div style='font-family: sans-serif; font-size: 13px; padding: 6px 10px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>"
                f"<b style='color: #345435;'>{building}</b><br>"
                f"<span style='color: #888;'>{count} responses</span>"
                f"</div>",
                sticky=True,
            ),
        ).add_to(m)

m.save("campus_heatmap.html")
print("saved")