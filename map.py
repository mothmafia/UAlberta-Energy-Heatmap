import folium
from folium.plugins import HeatMap
from heatmap import counts, BUILDING_COORDS

# create map
m = folium.Map(
    tiles="CartoDB positron",
    min_zoom = 13,
    max_zoom = 19,
)

# dynamically fit buildings
active_coords = [BUILDING_COORDS[b] for b in counts.index if b in BUILDING_COORDS]
if active_coords:
    m.fit_bounds(active_coords)

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
        transition: top 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    .title-card:hover {
        top: 0px;
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