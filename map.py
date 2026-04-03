import folium
import pandas as pd
from folium.plugins import HeatMap
import json
from heatmap import counts, counts_by_window, BUILDING_COORDS, CRASH_WINDOWS, df, energy_pct_by_window, energy_pct_total

# serialize window data
window_data_json = json.dumps({w: [
    [BUILDING_COORDS[b][0], BUILDING_COORDS[b][1], int(c)]
    for b, c in counts_by_window[w].items()
    if b in BUILDING_COORDS
] for w in CRASH_WINDOWS})
windows_json = json.dumps(CRASH_WINDOWS)

# serialize building counts, per time-window
window_counts_json = json.dumps({w: {
    b.strip().lower(): int(c)
    for b, c in counts_by_window[w].items()
    if b in BUILDING_COORDS
} for w in CRASH_WINDOWS})

total_counts_json = json.dumps({
    b.strip().lower(): int(c)
    for b, c, in counts.items()
})

coords_to_building_json = json.dumps({
    f"{lat}_{lng}": building
    for building, (lat, lng) in BUILDING_COORDS.items()
    if counts.get(building, 0) > 0
})
# serialize energy data
energy_pct_json = json.dumps(energy_pct_by_window)
energy_pct_total_json = json.dumps(energy_pct_total)

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
        white-space: nowrap;
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
        bottom: 24px;
        left: 20px;
        z-index: 1000;
        background: rgba(255,255,255,0.75);
        padding: 8px 12px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-family: sans-serif;
        overflow: hidden;
        transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
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
    .legend-stats {{
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid rgba(0,0,0,0.06);
        font-size: 9px;
        color: #bbb;
    }}
    @media (max-width: 695px) {{
        .legend-card {{
            bottom: 100px;
            left: 10px;
        }}
    }}
</style>
<div class="legend-card" id="legendCard">
    <div id="legendBase">
        <div class="legend-bar"></div>
        <div class="legend-labels">
        <span>low</span>
        <span>high</span>
    </div>
        <div class="legend-count">{len(df)} students surveyed</div>
        <div class="legend-count">last updated: {last_updated}</div>
    </div>
    <div class="legend-stats" id="legendStats">
        <div>top crash spots: placeholder</div>
        <div>X% drink energy drinks regularly</div>
    </div>
</div>

<script>
    (function() {{
        var card = document.getElementById("legendCard");
        var collapseTimer = null;

        function getCollapsedHeight() {{
            return document.getElementById("legendBase").scrollHeight + 16;
        }}

        function getExpandedHeight() {{
            return card.scrollHeight;
        }}

        window.addEventListener("load", function() {{
            card.style.height = getCollapsedHeight() + "px";
        }});

        card.addEventListener("mouseenter", function() {{
            if (collapseTimer) {{
                clearTimeout(collapseTimer); 
                collapseTimer = null;
            }}
            card.style.height = getExpandedHeight() + "px";
        }});

        card.addEventListener("mouseleave", function() {{
            collapseTimer = setTimeout(function() {{
                card.style.height = getCollapsedHeight() + "px";
            }}, 2000);
        }});
    }})();
</script>
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
for building, (lat, lng) in BUILDING_COORDS.items():
    count = counts.get(building, 0)
    if count > 0:
        folium.CircleMarker(
            location=[lat, lng],
            radius=6,
            color="white",
            weight=2,
            fill=True,
            fill_color="rgba(255,255,255,0.15)",
            fill_opacity=1,
            name=building,
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
        width: clamp(200px, 50vw, 420px);
        box-sizing: border-box;
    }}
    .tl-credit {{
        text-align: center;
        font-size: 9px;
        color: #bbb;
        margin-top: 4px;
    }}
    .tl-credit a {{
        color: #bbb;
        text-decoration: none;
        font-weight: 600;
    }}
    .tl-credit a:hover {{
        color: #345435;
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
    @media (max-width: 695px) {{
        .tl-bar {{
            left: 50%;
            bottom: 24px;
            width: calc(100vw - 32px);
        }}
    }}
</style>
<div class="tl-bar" id="tlBar">
    <div class="tl-labels" id="tlLabels"></div>
    <div class="tl-allday" id="tlAllDay">All Time</div>
</div>

<style>
    .credit {{
        position: fixed;
        bottom: 24px;
        right: 20px;
        z-index: 1000;
        background: rgba(255,255,255,0.75);
        padding: 6px 10px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-family: sans-serif;
        font-size: 9px;
        color: #bbb;
        white-space: nowrap;
    }}
    .credit a {{
        color: #345435;
        text-decoration: none;
        font-weight: 600;
    }}
    .credit a:hover {{
        color: #223823;
    }}
    @media (max-width: 695px) {{
        .credit {{
            display: none;
        }}
    }}
</style>
<div class="credit">
    made by <a href="https://www.linkedin.com/in/layan-a-4457713a0/" target="_blank">layan al-hamarneh</a>
</div>

<div id="custom-tooltip" style="
    display: none;
    position: fixed;
    z-index: 2000;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    padding: 6px 10px;
    font-family: sans-serif;
    font-size: 13px;
    pointer-events: none;
">
    <b id="tt-building" style="color: #345435;"></b><br>
    <span id="tt-count" style="color: #888;"></span>
</div>

<script>
    var WINDOWS = {windows_json};
    var SHORT_LABELS = {short_labels_json};
    var WINDOW_DATA = {window_data_json};
    var WINDOW_COUNTS = {window_counts_json};
    var TOTAL_COUNTS = {total_counts_json};
    var COORDS_TO_BUILDING = {coords_to_building_json};
    var ENERGY_PCT = {energy_pct_json};
    var ENERGY_PCT_TOTAL = {energy_pct_total_json};
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

        // custom tooltips because FOLIUM SUCKS
        var tooltip = document.getElementById("custom-tooltip");
        var ttBuilding = document.getElementById("tt-building");
        var ttCount = document.getElementById("tt-count");

        map.eachLayer(function(layer) {{
            if (layer._latlng) {{
                var key = layer._latlng.lat + "_" + layer._latlng.lng;
                var building = COORDS_TO_BUILDING[key];
                if (building) {{
                    layer.on("mouseover", function(e) {{
                        var buildingKey = building.trim().toLowerCase();
                        var count = activeIdx === -1
                            ? TOTAL_COUNTS[buildingKey]
                            : (WINDOW_COUNTS[WINDOWS[activeIdx]][buildingKey] || 0);
                    ttBuilding.textContent = building;
                    ttCount.textContent = count + " responses";
                    tooltip.style.display = "block";
                    tooltip.style.left = e.originalEvent.clientX + 12 + "px";
                    tooltip.style.top = e.originalEvent.clientY + 12 + "px";
                }});
                layer.on("mousemove", function(e) {{
                    tooltip.style.left = e.originalEvent.clientX + 12 + "px";
                    tooltip.style.top = e.originalEvent.clientY + 12 + "px";
                }});
                layer.on("mouseout", function() {{
                    tooltip.style.display = "none";
                }});
            }}
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
            var topBuildings, energyPct;

            if (idx === -1) {{
                // all time
                var sorted = Object.entries(TOTAL_COUNTS).sort((a, b) => b[1] - a[1]);
                topBuildings = sorted.slice(0, 2).map(e => e[0]).join(", ");
                energyPct = ENERGY_PCT_TOTAL;
            }} else {{
                // by window
                var windowCounts = WINDOW_COUNTS[WINDOWS[idx]] || {{}};
                var sorted = Object.entries(windowCounts).sort((a, b) => b[1] - a[1]);
                topBuildings = sorted.slice(0, 2).map(e => e[0]).join(", ");
                energyPct = ENERGY_PCT[WINDOWS[idx]] || 0;
            }}

            var stats = document.getElementById("legendStats");
            if (stats) {{
                stats.children[0].textContent = "top crash spots: " + topBuildings;
                stats.children[1].textContent = energyPct + "% drink energy drinks regularly";
            }}

            document.querySelectorAll(".tl-slot").forEach(function(btn, i) {{
                btn.classList.toggle("active", i === idx);
            }});

            // tooltips show window counts
            var counts = idx === -1 ? null : WINDOW_COUNTS[WINDOWS[idx]];
            document.querySelectorAll(".marker-tip").forEach(function(tip) {{
                var building = tip.getAttribute("data-building").trim().toLowerCase();
                var countEl = tip.querySelector(".marker-count");
                if (countEl) {{
                    var count = counts ? (counts[building] || 0) : TOTAL_COUNTS[building];
                    countEl.textContent = count + " responses";
                }}
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

        showWindow(-1);
    }}, 1000);
</script>
"""
m.get_root().html.add_child(folium.Element(timeline_html))

m.save("campus_heatmap.html")
print("saved")
print(df.columns.tolist())
print(df['What time of day do you crash the hardest?'].unique())