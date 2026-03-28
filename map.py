import folium
import pandas as pd
from folium.plugins import HeatMap
import json
from heatmap import counts, counts_by_window, BUILDING_COORDS, CRASH_WINDOWS, df

# serialize window data
window_data_json = json.dumps({w: [
    [BUILDING_COORDS[b][0], BUILDING_COORDS[b][1], int(c)]
    for b, c in counts_by_window[w].items()
    if b in BUILDING_COORDS
] for w in CRASH_WINDOWS})
windows_json = json.dumps(CRASH_WINDOWS)

# serialize building counts, per time-window
window_counts_json = json.dumps({w: {
    b: int(c)
    for b, c in counts_by_window[w].items()
    if b in BUILDING_COORDS
} for w in CRASH_WINDOWS})

# cleaner timeline labels
SHORT_LABELS = ["< 10AM", "10AM", "12PM", "2PM", "5PM+"]
short_labels_json = json.dumps(SHORT_LABELS)

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
        color: #345435;
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

# credit hehe
credit_html = """
<style>
    .credit-card {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        background: rgba(255,255,255,0.75);
        padding: 6px 12px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-family: sans-serif;
        font-size: 10px;
        color: #345435;
    }
    .credit-card a {
        color: #345435;
        text-decoration: none;
        font-weight: 600;
    }
    .credit-card a:hover {
        text-decoration: underline;
    }
</style>
<div class="credit-card">
    made by <a href="https://www.linkedin.com/in/layan-a-4457713a0/?skipRedirect=true" target="_blank">layan al-hamarneh</a>
</div>
"""
m.get_root().html.add_child(folium.Element(credit_html))

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

# timeline bar
timeline_html = f"""
<style>
    .tl-bar {{
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        background: rgba(255,255,255,0.75);
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        padding: 10px 16px;
        font-family: sans-serif;
        min-width: 320px;
    }}
    .tl-controls {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 6px;
    }}
    .tl-play {{
        background: none;
        border: none;
        color: #345435;
        font-size: 14px;
        cursor: pointer;
        padding: 0;
        flex-shrink: 0;
    }}
    .tl-track {{
        flex: 1;
        height: 3px;
        background: #ddd;
        border-radius: 2px;
        position: relative;
    }}
    .tl-fill {{
        height: 100%;
        width: 0%;
        background: #345435;
        border-radius: 2px;
        transition: width 0.4s ease;
    }}
    .tl-thumb {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #345435;
        position: absolute;
        top: 50%;
        left: 0%;
        transform: translate(-50%, -50%);
        transition: left 0.4s ease;
    }}
    .tl-labels {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
    }}
    .tl-slot {{
        font-size: 10px;
        color: #888;
        cursor: pointer;
        transition: color 0.2s;
    }}
    .tl-slot:hover {{ color: #345435; }}
    .tl-slot.active {{ color: #345435; font-weight: 600;}}
    .tl-allday {{
        text-align: center;
        font-size: 10px;
        color: #aaa;
        cursor: pointer;
        transition: color 0.2s;
    }}
    .tl-allday:hover {{ color: #345435; }}
</style>
<div class="tl-bar" id="tlBar">
    <div class="tl-controls">
        <button class="tl-play" id="tlPlay">&#9654;</button>
        <div class="tl-track">
            <div class="tl-fill" id="tlFill"></div>
            <div class="tl-thumb" id="tlThumb"></div>
        </div>
    </div>
    <div class="tl-labels" id="tlLabels"></div>
    <div class="tl-allday" id="tlAllDay">All day</div>
</div>

<script>
    var WINDOWS = {windows_json};
    var SHORT_LABELS = {short_labels_json};
    var WINDOW_DATA = {window_data_json};
    var currentLayer = null;
    var activeIdx = -1;

    var slots = document.getElementById("tlLabels");
    SHORT_LABELS.forEach(function(label, i) {{
        var btn = document.createElement("div");
        btn.className = "tl-slot";
        btn.textContent = label;
        slots.appendChild(btn);
    }});

    setTimeout(function() {{
        var map = Object.values(window).find(function(v) {{
            return v && v._leaflet_id && v.addLayer;
        }});

        var baseLayer = null;
        map.eachLayer(function(layer) {{
            if (layer.options && layer.options.gradient) {{
                baseLayer = layer;
            }}
        }});

        function showWindow(idx) {{
            if (currentLayer) {{
                map.removeLayer(currentLayer);
                currentLayer = null;
            }}

            if (idx !== -1) {{
                if (baseLayer) map.removeLayer(baseLayer);

                var pts = WINDOW_DATA[WINDOWS[idx]];
                if (pts && pts.length > 0) {{
                    currentLayer = L.heatLayer(pts, {{
                        radius: 50, blur: 40, minOpacity: 0.3,
                        gradient: {{0.0: "#C9B8F5", 0.3: "#89A4F7", 0.6: "#F4A89A", 1.0: "#F5C842"}}
                    }}).addTo(map);
                }}
            }} else {{
                if (baseLayer) map.addLayer(baseLayer);
            }}

            activeIdx = idx;
            document.querySelectorAll(".tl-slot").forEach(function(btn, i) {{
                btn.classList.toggle("active", i === idx);
            }});
        }}

        document.querySelectorAll(".tl-slot").forEach(function(btn, i) {{
            btn.onclick = function() {{ showWindow(i); }};
        }});

        var allDay = document.getElementById("tlAllDay");
        if (allDay) {{
            allDay.onclick = function() {{
                showWindow(-1);
            }};
        }}

    }}, 500);
</script>
"""
m.get_root().html.add_child(folium.Element(timeline_html))

m.save("campus_heatmap.html")
print("saved")