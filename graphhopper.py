#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#From Team DevOps

#HEART GOLLOSO
#The program demonstrates excellent integration of the Graphhopper API with a user-friendly Tkinter interface, effectively combining routing, geocoding, 
#and map visualization. Features such as dark mode, multithreaded report generation, and turn-by-turn directions reflect strong technical skills and 
#attention to user experience. The system’s clean layout and responsiveness make it both functional and engaging for users.
#RECOMMENDATIONS 
#To further improve the system, it is recommended to modularize the code for easier maintenance and apply advanced error handling and 
#caching for reliability. Securing the API key using environment variables and allowing PDF report exports or dropdown vehicle selection would 
#enhance usability and security. Adding real-time traffic updates or CO₂ emission estimation could also make the system more dynamic and 
#sustainable in future versions.

"""
CARL LAWRENCE CHUA
Clean modular logic for geocoding, routing, and UI.
Effective use of threading to keep the interface responsive.
Well-designed and user-friendly HTML report with light/dark mode.
Accurate travel, fuel, and energy calculations.

Split into multiple modules for better maintainability.
Add try-except-finally to guarantee modal closure during errors.
Use None instead of strings like "null" for failed coordinates.
Implement retry logic for API calls and add CO₂ emission estimates.
Escape user input in HTML to prevent potential injection.
"""

#KING WHESTLIE YEMA
#This report-focused Tkinter tool feels thoughtfully engineered: the threaded workflow keeps the UI responsive, the loading
#modal communicates progress, and the HTML report balances clarity (KPIs, turn icons, theme toggle) with polish (SVG pins,
#mode-aware colors). Philippine defaults and energy/calorie estimates add practical, local relevance. The tile fallback and
#defensive parsing help the experience remain stable even on flaky networks.
#RECOMMENDATIONS
#Add debounced autocomplete for Origin/Destination (show top geocoder hits) to reduce typos and speed up entry.
#Include an in-app “Preview report” pane or quick-open button with a success/failure toast after file write completes.
#Provide a print-optimized stylesheet and a one-click “Download PDF” (window.print()) layout for the HTML report.
#Expose a small “What-if” panel in the report to adjust fuel price/efficiency live and recalc cost without re-running the app.
#Persist user preferences (last O/D, vehicle, theme, default prices) in a settings JSON and restore on launch.
#Harden network calls with per-request timeouts, limited retries with jitter, and a circuit-breaker after repeated failures.
#Add automated checks: validate that build_report_html outputs a complete document and that dark-mode toggle updates map/polyline.
#Package a distributable build (PyInstaller single-file), ensuring all SVG/JS assets are inlined so reports still render when shared.
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# COMMENTS from Team Devnet & Chill - Via
# The app’s design is simple yet practical, making it easy to use even for beginners. To make it more user-centered, 
# it would be helpful if the system could remember the last searched origin, destination, and chosen vehicle type. 
# Saving these preferences locally or in a small settings file (e.g., JSON) would reduce repetitive inputs. 
# A “Recent Reports” or “History” dropdown could let users quickly re-open previous routes for review or comparison.
# Add route options toggles (e.g., “Avoid tolls/ferries/highways”) so users can tailor paths without changing origin/destination.
# Provide a one-click “Share route” button that copies a prefilled link (origin, destination, vehicle, theme) to quickly reopen the same report.
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#!/usr/bin/env python3
# graphhopper_visual_report_only.py
# Enhanced GUI for Graphhopper routing → report.html
# - Uses Philippine market pump prices as defaults (Oct 2025)
# - Calories estimated automatically (no user input)
# - Loading modal while generating report (threaded)
# - Turn icons, fuel/calorie/ebike energy, dark mode, more vehicles
# - IMPROVED: Realistic vehicle icons, color-coded directions, proper pin markers
#
# Usage: python3 graphhopper_visual_report_only.py
# Requires: requests, tkinter (standard lib), webbrowser, threading

import os
import json
import webbrowser
import urllib.parse
from datetime import timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time

ROUTE_URL = "https://graphhopper.com/api/1/route?"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"

# Fallback API key (keep out of source in production)
DEFAULT_API_KEY = "05ddb74c-90fe-4dad-9236-e37bb1fc2003"

# ===== PHILIPPINE MARKET DEFAULTS (sourced Oct 13, 2025) =====
DEFAULT_GASOLINE_PHP_PER_L = 57.20
DEFAULT_DIESEL_PHP_PER_L = 55.45
DEFAULT_FUEL_EFF_L100 = 7.0
DEFAULT_WEIGHT_KG = 70.0

DIRECTION_COLORS = {
    "turn-left": "#FF6B6B",      # Red
    "turn-right": "#4ECDC4",     # Teal
    "straight": "#45B7D1",       # Blue
    "roundabout": "#F7B731",     # Golden
    "uturn": "#E74C3C",          # Dark Red
    "end": "#2ECC71",            # Green
}

# --- Helpers ---
def get_api_key() -> str:
    return os.getenv("GRAPHHOPPER_API_KEY", DEFAULT_API_KEY)

def km_to_miles(km: float) -> float:
    return km / 1.60934

def format_duration_ms(ms: int) -> str:
    td = timedelta(milliseconds=ms)
    total_seconds = int(td.total_seconds())
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def geocode(location: str, api_key: str):
    """Return: (status_code, lat, lng, label)"""
    url = GEOCODE_URL + urllib.parse.urlencode({"q": location, "limit": "1", "key": api_key})
    try:
        r = requests.get(url, timeout=20)
        data = r.json() if "application/json" in r.headers.get("content-type", "") else {}
        if r.status_code == 200 and data.get("hits"):
            hit = data["hits"][0]
            lat = hit["point"]["lat"]
            lng = hit["point"]["lng"]
            name = hit.get("name") or hit.get("osm_value") or location
            state = hit.get("state", "")
            country = hit.get("country", "")
            parts = [p for p in [name, state, country] if p]
            label = ", ".join(parts)
            return 200, lat, lng, label
        return r.status_code, "null", "null", location
    except Exception as e:
        return 0, "null", "null", f"{location} (error: {e})"

SVG_ICONS = {
    "turn-left": """<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 7l-6 5 6 5V11h6V7z" fill="#FF6B6B" /></svg>""",
    "turn-right": """<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 7l6 5-6 5V11H4V7z" fill="#4ECDC4" /></svg>""",
    "straight": """<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2v20M8 18l4 4 4-4" stroke="#45B7D1" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" /></svg>""",
    "roundabout": """<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" stroke="#F7B731" stroke-width="2" fill="none"/><path d="M12 4v-2l2 2-2 2" fill="#F7B731"/></svg>""",
    "uturn": """<svg width="24" height="24" viewBox="0 0 24 24"><path d="M7 7v6a5 5 0 0 0 10 0" stroke="#E74C3C" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M17 7l-2-2 2-2" stroke="#E74C3C" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
    "end": """<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" fill="#2ECC71"/></svg>""",
    "dot": """<svg width="20" height="20" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" fill="#999"/></svg>""",
    
    "start-pin": """<svg width="32" height="40" viewBox="0 0 32 40" xmlns="http://www.w3.org/2000/svg"><path d="M16 0C7.2 0 0 6.8 0 16c0 8 16 24 16 24s16-16 16-24c0-9.2-7.2-16-16-16z" fill="#22C55E"/><circle cx="16" cy="16" r="6" fill="white"/></svg>""",
    "end-pin": """<svg width="32" height="40" viewBox="0 0 32 40" xmlns="http://www.w3.org/2000/svg"><path d="M16 0C7.2 0 0 6.8 0 16c0 8 16 24 16 24s16-16 16-24c0-9.2-7.2-16-16-16z" fill="#EF4444"/><circle cx="16" cy="16" r="6" fill="white"/></svg>""",
    
    "vehicle-car": """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="9" width="18" height="8" rx="2" fill="#3B82F6"/><rect x="5" y="7" width="14" height="3" rx="1" fill="#3B82F6"/><circle cx="6" cy="17" r="1.5" fill="#1F2937"/><circle cx="18" cy="17" r="1.5" fill="#1F2937"/><rect x="7" y="8" width="3" height="2" fill="#93C5FD"/><rect x="14" y="8" width="3" height="2" fill="#93C5FD"/></svg>""",
    "vehicle-bike": """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="6" cy="16" r="3" fill="none" stroke="#10B981" stroke-width="1.5"/><circle cx="18" cy="16" r="3" fill="none" stroke="#10B981" stroke-width="1.5"/><path d="M12 8L6 16M12 8L18 16M12 8L12 4" stroke="#10B981" stroke-width="1.5" fill="none"/><circle cx="12" cy="8" r="1.5" fill="#10B981"/></svg>""",
    "vehicle-motorcycle": """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="5" cy="16" r="2.5" fill="none" stroke="#F59E0B" stroke-width="1.5"/><circle cx="19" cy="16" r="2.5" fill="none" stroke="#F59E0B" stroke-width="1.5"/><path d="M5 16L12 8L19 16" stroke="#F59E0B" stroke-width="1.5" fill="none"/><rect x="10" y="6" width="4" height="4" rx="1" fill="#F59E0B"/><line x1="12" y1="10" x2="12" y2="16" stroke="#F59E0B" stroke-width="1.5"/></svg>""",
    "vehicle-truck": """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="10" width="12" height="8" rx="1" fill="#8B5CF6"/><rect x="14" y="12" width="8" height="6" rx="1" fill="#8B5CF6"/><circle cx="5" cy="18" r="1.5" fill="#1F2937"/><circle cx="17" cy="18" r="1.5" fill="#1F2937"/><rect x="14" y="10" width="8" height="2" fill="#A78BFA"/></svg>""",
    "vehicle-ebike": """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="6" cy="16" r="3" fill="none" stroke="#06B6D4" stroke-width="1.5"/><circle cx="18" cy="16" r="3" fill="none" stroke="#06B6D4" stroke-width="1.5"/><path d="M12 8L6 16M12 8L18 16M12 8L12 4" stroke="#06B6D4" stroke-width="1.5" fill="none"/><circle cx="12" cy="8" r="1.5" fill="#06B6D4"/><rect x="10" y="11" width="4" height="2" rx="0.5" fill="#FBBF24"/></svg>""",
    "vehicle-scooter": """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="6" cy="18" r="2" fill="none" stroke="#EC4899" stroke-width="1.5"/><circle cx="16" cy="18" r="2" fill="none" stroke="#EC4899" stroke-width="1.5"/><path d="M6 18L14 8L16 18" stroke="#EC4899" stroke-width="1.5" fill="none"/><rect x="13" y="6" width="3" height="4" rx="1" fill="#EC4899"/></svg>""",
    "vehicle-foot": """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="4" r="1.5" fill="#6366F1"/><path d="M12 6v6M12 12l-3 6M12 12l3 6" stroke="#6366F1" stroke-width="1.5" stroke-linecap="round"/><path d="M9 18l-1 4M15 18l1 4" stroke="#6366F1" stroke-width="1.5" stroke-linecap="round"/></svg>""",
}

VEHICLE_TO_SVG_KEY = {
    "car": "vehicle-car",
    "bike": "vehicle-bike",
    "foot": "vehicle-foot",
    "motorcycle": "vehicle-motorcycle",
    "truck": "vehicle-truck",
    "ebike": "vehicle-ebike",
    "scooter": "vehicle-scooter",
}


# --- Logic (threaded) ---
def run_route_threaded(root, origin, dest, vehicle, status_var, options, loading_modal):
    """
    This function runs inside a Thread. It updates GUI via root.after to remain thread-safe.
    """
    api_key = get_api_key()
    
    def set_status(s):
        root.after(0, status_var.set, s)

    set_status("Geocoding...")
    s1, lat1, lng1, label1 = geocode(origin, api_key)
    s2, lat2, lng2, label2 = geocode(dest, api_key)

    if not (s1 == 200 and s2 == 200):
        root.after(0, messagebox.showerror, "Error", "Geocoding failed. Try clearer names.")
        set_status("Ready")
        root.after(0, close_loading_modal, loading_modal, None)
        return

    base_params = {
        "key": api_key,
        "vehicle": vehicle,
        "points_encoded": "false",
        "instructions": "true",
    }
    op = f"&point={lat1}%2C{lng1}"
    dp = f"&point={lat2}%2C{lng2}"
    url = ROUTE_URL + urllib.parse.urlencode(base_params) + op + dp

    set_status("Getting route...")
    try:
        r = requests.get(url, timeout=40)
        data = r.json()
    except Exception as e:
        root.after(0, messagebox.showerror, "Error", f"Route request failed: {e}")
        set_status("Ready")
        root.after(0, close_loading_modal, loading_modal, None)
        return

    if r.status_code != 200 or "paths" not in data:
        root.after(0, messagebox.showerror, "Error", f"Routing failed: {data.get('message','Unknown error')}")
        set_status("Ready")
        root.after(0, close_loading_modal, loading_modal, None)
        return

    path = data["paths"][0]
    set_status("Calculating metrics...")

    distance_km = safe_float(path.get("distance", 0)) / 1000.0
    duration_min = (safe_float(path.get("time", 0)) / 1000.0) / 60.0

    fuel_info = None
    calories_info = None

    # Choose a sensible default price based on vehicle type (car uses gasoline, truck uses diesel)
    if vehicle in ("car", "motorcycle", "scooter"):
        price_default = options.get("fuel_price_overridden") or DEFAULT_GASOLINE_PHP_PER_L
    elif vehicle in ("truck",):
        price_default = options.get("fuel_price_overridden") or DEFAULT_DIESEL_PHP_PER_L
    else:
        price_default = options.get("fuel_price_overridden") or DEFAULT_GASOLINE_PHP_PER_L

    if vehicle in ("car", "truck", "motorcycle"):
        eff = safe_float(options.get("fuel_eff_l100", DEFAULT_FUEL_EFF_L100))
        price = safe_float(options.get("fuel_price_per_l", price_default))
        fuel_info = estimate_fuel_and_cost(distance_km, eff, price)
        fuel_info["price_per_liter"] = price

    # Automatic calorie estimation — no user input required
    weight = DEFAULT_WEIGHT_KG
    if vehicle in ("foot", "bike", "ebike"):
        calories_info = estimate_calories(duration_min, weight, vehicle)
        if vehicle == "ebike":
            ebike_kwh = estimate_ebike_energy(distance_km)
            calories_info["ebike_kwh"] = ebike_kwh

    set_status("Creating report...")
    theme = "dark" if options.get("dark_mode") else "light"
    try:
        report = build_report_html(label1, label2, vehicle, path, "report.html", theme=theme, fuel_info=fuel_info, calories_info=calories_info)
        abs_path = os.path.abspath(report)
        webbrowser.open(f"file://{abs_path}")
        set_status("Done")
    except Exception as e:
        root.after(0, messagebox.showerror, "Error", f"Report generation failed: {e}")
        set_status("Ready")
    finally:
        root.after(0, close_loading_modal, loading_modal, None)

# --- Calculations helpers ---
def estimate_fuel_and_cost(distance_km: float, eff_l_per_100km: float, price_per_liter: float):
    """
    Estimate the fuel consumption (liters) and cost based on the distance, fuel efficiency,
    and price per liter.
    """
    liters = (distance_km * eff_l_per_100km) / 100.0  # Fuel consumption in liters
    cost = liters * price_per_liter if price_per_liter is not None else None  # Total cost
    return {"liters": liters, "cost": cost, "eff_l_per_100km": eff_l_per_100km, "price_per_liter": price_per_liter}

def estimate_calories(duration_minutes: float, body_weight_kg: float, activity_type: str):
    """
    Estimate calorie expenditure for active transportation based on MET values.
    """
    met_values = {
        'walking': 3.5,
        'foot': 3.5,
        'cycling': 7.0,
        'bike': 7.0,
        'ebike': 4.0,
    }
    met = met_values.get(activity_type.lower(), 3.5)
    duration_hours = duration_minutes / 60.0
    kcal = met * body_weight_kg * duration_hours
    return {"kcal": kcal, "note": f"Based on {activity_type} at {met} METs"}

def estimate_ebike_energy(distance_km: float):
    """
    Estimate energy consumption for e-bikes (typical 15-20 Wh/km).
    """
    wh_per_km = 17.5  # Average e-bike consumption
    kwh = (distance_km * wh_per_km) / 1000.0
    return kwh

def instruction_icon_for_text(text: str):
    """
    Return icon key and color for direction text
    """
    t = text.lower()
    if "roundabout" in t or "rotary" in t:
        return "roundabout"
    if "u-turn" in t or "u turn" in t or "uturn" in t:
        return "uturn"
    if "left" in t:
        return "turn-left"
    if "right" in t:
        return "turn-right"
    if "continue" in t or "straight" in t or "head" in t or "onto" in t:
        return "straight"
    if "arrive" in t or "destination" in t:
        return "end"
    return "dot"

# --- Threaded worker + loading modal helpers ---
def open_loading_modal(root, title="Generating report..."):
    modal = tk.Toplevel(root)
    modal.title(title)
    modal.geometry("320x90")
    modal.resizable(False, False)
    modal.transient(root)
    modal.grab_set()
    frm = ttk.Frame(modal, padding=12)
    frm.pack(fill="both", expand=True)
    lbl = ttk.Label(frm, text=title)
    lbl.pack(pady=(0,8))
    pb = ttk.Progressbar(frm, mode="indeterminate")
    pb.pack(fill="x")
    pb.start(10)
    # Provide reference to widgets so caller can close
    return modal, pb

def close_loading_modal(modal, pb=None):
    try:
        if pb:
            pb.stop()
    except Exception:
        pass
    try:
        modal.grab_release()
        modal.destroy()
    except Exception:
        pass

def safe_get_points(coords):
    try:
        return [[c[1], c[0]] for c in coords]
    except Exception:
        return []

def build_report_html(
    origin_label: str,
    dest_label: str,
    vehicle: str,
    path: dict,
    outfile: str = "report.html",
    theme: str = "light",
    fuel_info: dict = None,
    calories_info: dict = None,
):
    km = safe_float(path.get("distance", 0.0)) / 1000.0
    miles = km_to_miles(km)
    duration_ms = int(path.get("time", 0) or 0)
    duration_str = format_duration_ms(duration_ms)
    steps = path.get("instructions", []) or []
    coords = path.get("points", {}).get("coordinates", []) or []

    latlon = safe_get_points(coords)
    
    rows = ""
    for i, s in enumerate(steps):
        text = s.get("text", "")
        dist_km = (safe_float(s.get("distance", 0)) / 1000.0)
        icon_key = instruction_icon_for_text(text)
        icon_svg = SVG_ICONS.get(icon_key, SVG_ICONS["dot"])
        icon_color = DIRECTION_COLORS.get(icon_key, "#999")
        
        rows += (
            "<tr>"
            f"<td style='width:42px; text-align:center; border-left: 4px solid {icon_color}'>{icon_svg}</td>"
            f"<td style='min-width:200px'>{text}</td>"
            f"<td style='white-space:nowrap'>{dist_km:.2f} km</td>"
            "</tr>"
        )

    veh_svg = SVG_ICONS.get(VEHICLE_TO_SVG_KEY.get(vehicle, ""), SVG_ICONS["dot"])

    fuel_html = ""
    if fuel_info:
        liters = fuel_info.get("liters", 0.0)
        price = fuel_info.get("cost")
        eff = fuel_info.get("eff_l_per_100km")
        price_per_l = fuel_info.get("price_per_liter")
        fuel_html = f"<div class='pill'>Fuel: {liters:.2f} L (eff {eff:.1f} L/100km)</div>"
        if price is not None and price_per_l is not None:
            fuel_html += f"<div class='pill'>Cost: ₱{price:.2f} (₱{price_per_l:.2f}/L)</div>"

    calories_html = ""
    if calories_info:
        kcal = calories_info.get("kcal", 0.0)
        note = calories_info.get("note", "")
        calories_html = f"<div class='pill'>Calories: {kcal:.0f} kcal</div>"
        if note:
            calories_html += f"<div style='font-size:12px;margin-top:6px;color:#666'>{note}</div>"

    ebike_html = ""
    if calories_info and calories_info.get("ebike_kwh") is not None:
        kwh = calories_info.get("ebike_kwh")
        ebike_html = f"<div class='pill'>E-bike energy: {kwh:.2f} kWh</div>"

    dark_css = ""
    body_class = ""
    if theme == "dark":
        body_class = "dark"
        dark_css = """
        :root { 
            --bg: #121212; 
            --card: #1e1e1e; 
            --text: #e4e4e4; 
            --muted: #a0a0a0; 
            --accent: #4db380; 
            --pill: #1a2b22; 
            --header: #2c6e49;
            --border: #2d2d2d;
            --table-border: #333;
            --table-header: #252525;
        }
        body.dark header { 
            background: var(--header); 
            color: #eee; 
            box-shadow: 0 1px 10px rgba(0,0,0,0.4);
        }
        body.dark { 
            background: var(--bg); 
            color: var(--text); 
        }
        body.dark .card { 
            background: var(--card); 
            color: var(--text); 
            box-shadow: 0 6px 18px rgba(0,0,0,0.4); 
            border: 1px solid var(--border);
        }
        body.dark table th { 
            background: var(--table-header); 
            border-bottom: 1px solid var(--border);
        }
        body.dark table td {
            border-bottom: 1px solid var(--table-border);
        }
        body.dark .pill { 
            background: var(--pill); 
            border-color: #2d3f35; 
            color: #a4d5c1; 
        }
        body.dark a {
            color: #68c3fd;
        }
        body.dark .dark-mode-toggle {
            background: rgba(255,255,255,0.2);
        }
        body.dark .dark-mode-toggle:hover {
            background: rgba(255,255,255,0.25);
        }
        """
    else:
        dark_css = """
        .dark-mode-toggle {
            background: rgba(0,0,0,0.1);
        }
        .dark-mode-toggle:hover {
            background: rgba(0,0,0,0.15);
        }
        """

    html = f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<title>Route Report</title>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' crossorigin=''/>
<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js' crossorigin=''></script>
<style>
{dark_css}
body {{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#fafafa;margin:0;padding:0}}
header {{background:#0b6;color:white;padding:16px 24px;display:flex;align-items:center;justify-content:space-between}}
.header-left {{display:flex;gap:16px;align-items:center}}
.dark-mode-toggle {{padding:8px 14px;border-radius:8px;cursor:pointer;user-select:none;display:flex;align-items:center;gap:8px;font-weight:500;transition:all 0.2s ease}}
.dark-mode-toggle:hover {{background:rgba(0,0,0,0.15)}}
.dark-mode-icon {{width:20px;height:20px;display:flex;align-items:center;justify-content:center}}
.wrap {{padding:16px 24px}}
.grid {{display:grid;grid-template-columns:2fr 1fr;gap:16px}}
.card {{background:white;border-radius:12px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
#map {{height:520px;width:100%;border-radius:10px}}
table {{width:100%;border-collapse:collapse;font-size:14px}}
th,td {{padding:8px 6px;border-bottom:1px solid #eee;text-align:left;vertical-align:middle}}
th {{background:#f6f6f6}}
.kpi {{display:flex;gap:12px;flex-wrap:wrap}}
.pill {{background:#eef9f1;border:1px solid #cdebd7;padding:8px 10px;border-radius:999px;font-weight:600}}
.vehicle-chip {{display:flex;gap:12px;align-items:center;background:rgba(255,255,255,0.15);padding:6px 10px;border-radius:10px}}
.header-title {{display:flex;flex-direction:column}}
</style>
</head>
<body class="{body_class}">
<header>
<div class="header-left">
  <div class="vehicle-chip" style="color:inherit">
    <div style="display:flex;align-items:center">{veh_svg}</div>
    <div class="header-title"><div style="font-weight:700">Vehicle: {vehicle}</div><div style="font-size:13px;color:rgba(255,255,255,0.9)">{origin_label} → {dest_label}</div></div>
  </div>
</div>
<div class="dark-mode-toggle" onclick="toggleDarkMode()">
  <div class="dark-mode-icon">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path id="moon-icon" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" style="display:{'none' if theme == 'dark' else 'block'}"></path>
      <circle id="sun-circle" cx="12" cy="12" r="5" style="display:{'block' if theme == 'dark' else 'none'}"></circle>
      <line id="sun-line-1" x1="12" y1="1" x2="12" y2="3" style="display:{'block' if theme == 'dark' else 'none'}"></line>
      <line id="sun-line-2" x1="12" y1="21" x2="12" y2="23" style="display:{'block' if theme == 'dark' else 'none'}"></line>
      <line id="sun-line-3" x1="4.22" y1="4.22" x2="5.64" y2="5.64" style="display:{'block' if theme == 'dark' else 'none'}"></line>
      <line id="sun-line-4" x1="18.36" y1="18.36" x2="19.78" y2="19.78" style="display:{'block' if theme == 'dark' else 'none'}"></line>
      <line id="sun-line-5" x1="1" y1="12" x2="3" y2="12" style="display:{'block' if theme == 'dark' else 'none'}"></line>
      <line id="sun-line-6" x1="21" y1="12" x2="23" y2="12" style="display:{'block' if theme == 'dark' else 'none'}"></line>
      <line id="sun-line-7" x1="4.22" y1="19.78" x2="5.64" y2="18.36" style="display:{'block' if theme == 'dark' else 'none'}"></line>
      <line id="sun-line-8" x1="18.36" y1="5.64" x2="19.78" y2="4.22" style="display:{'block' if theme == 'dark' else 'none'}"></line>
    </svg>
  </div>
  <span id="theme-text">{"Light" if theme == 'dark' else "Dark"} Mode</span>
</div>
</header>
<div class='wrap'>
<div class='grid'>
<div class='card'><div id='map'></div></div>
<div class='card'>
<h3>Summary</h3>
<div class='kpi'>
<div class='pill'>Distance: {miles:.1f} miles / {km:.1f} km</div>
<div class='pill'>Duration: {duration_str}</div>
{fuel_html}
{calories_html}
{ebike_html}
</div>
</div></div>
<div class='card' style='margin-top:16px'>
<h3>Turn-by-turn</h3>
<table><thead><tr><th style='width:48px'></th><th>Instruction</th><th style='width:110px'>Distance</th></tr></thead>
<tbody>{rows}</tbody></table></div></div>
<script>
try {{
  console.log('Initializing map...');
  const latlon = {json.dumps(latlon)};
  console.log('Coordinates loaded:', latlon.length > 0 ? 'Yes' : 'No', latlon.length);
  const isDarkMode = document.body.classList.contains('dark');
  
  // Check if the map container exists
  if (!document.getElementById('map')) {{
    console.error('Map container not found');
    throw new Error('Map container not found');
  }}
  
  const map = L.map('map').setView(latlon.length ? latlon[Math.floor(latlon.length/2)] : [0,0], latlon.length ? 12 : 2);
  console.log('Map initialized');
  
  // Choose map style based on theme
  const mapStyle = isDarkMode 
    ? 'https://cartodb-basemaps-{{s}}.global.ssl.fastly.net/dark_all/{{z}}/{{x}}/{{y}}.png'
    : 'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png';
  
  let tileLayer;
  
  try {{
    // Try the first map style
    console.log('Loading tiles from:', mapStyle);
    tileLayer = L.tileLayer(mapStyle, {{
      maxZoom: 19, 
      attribution: isDarkMode 
        ? '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
        : '&copy; OpenStreetMap contributors'
    }}).addTo(map);
    
    // Add an error handler
    tileLayer.on('tileerror', function(event) {{
      console.error('Tile error:', event);
      // If we get tile errors, try a different source
      if (!window.triedAlternativeSource) {{
        window.triedAlternativeSource = true;
        map.removeLayer(tileLayer);
        tileLayer = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          maxZoom: 19,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }}).addTo(map);
      }}
    }});
  }} catch (e) {{
    console.error('Error adding tile layer:', e);
    // Fallback to OpenStreetMap directly
    tileLayer = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }}).addTo(map);
  }}
  
  // Choose line color based on theme
  const lineColor = isDarkMode ? '#4db6ff' : '#0078ff';
  let line = L.polyline(latlon, {{color: lineColor, weight: 5, opacity: 0.8}}).addTo(map);
  // Define markers at global scope
  let startMarker, endMarker;
  
  if (latlon.length) {{
    const startIcon = L.icon({{
      iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCAzMiA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTYgMEM3LjIgMCAwIDYuOCAwIDE2YzAgOCAxNiAyNCAxNiAyNHMxNi0xNiAxNi0yNGMwLTkuMi03LjItMTYtMTYtMTZ6IiBmaWxsPSIjMjJDNTVFIi8+PGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iNiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=',
      iconSize: [32, 40],
      iconAnchor: [16, 40],
      popupAnchor: [0, -40]
    }});
    const endIcon = L.icon({{
      iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCAzMiA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTYgMEM3LjIgMCAwIDYuOCAwIDE2YzAgOCAxNiAyNCAxNiAyNHMxNi0xNiAxNi0yNGMwLTkuMi03LjItMTYtMTYtMTZ6IiBmaWxsPSIjRUY0NDQ0Ii8+PGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iNiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=',
      iconSize: [32, 40],
      iconAnchor: [16, 40],
      popupAnchor: [0, -40]
    }});
    startMarker = L.marker(latlon[0], {{icon: startIcon}}).addTo(map).bindTooltip("Start");
    endMarker = L.marker(latlon[latlon.length-1], {{icon: endIcon}}).addTo(map).bindTooltip("End");
    map.fitBounds(line.getBounds(), {{padding:[20,20]}});
  }}
  
  // Add dark mode toggle functionality
  function toggleDarkMode() {{
    document.body.classList.toggle('dark');
    const isDarkNow = document.body.classList.contains('dark');
    
    // Update theme text
    document.getElementById('theme-text').textContent = isDarkNow ? 'Light Mode' : 'Dark Mode';
    
    // Toggle icon visibility
    document.getElementById('moon-icon').style.display = isDarkNow ? 'none' : 'block';
    const sunElements = ['sun-circle', 'sun-line-1', 'sun-line-2', 'sun-line-3', 'sun-line-4', 'sun-line-5', 'sun-line-6', 'sun-line-7', 'sun-line-8'];
    sunElements.forEach(id => {{
      document.getElementById(id).style.display = isDarkNow ? 'block' : 'none';
    }});
    
    try {{
      // Update map style
      if (tileLayer) {{
        map.removeLayer(tileLayer);
      }}
      const newMapStyle = isDarkNow 
        ? 'https://cartodb-basemaps-{{s}}.global.ssl.fastly.net/dark_all/{{z}}/{{x}}/{{y}}.png'
        : 'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png';
      tileLayer = L.tileLayer(newMapStyle, {{
        maxZoom: 19, 
        attribution: isDarkNow 
          ? '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
          : '&copy; OpenStreetMap contributors'
      }}).addTo(map);
      
      // Update polyline color
      if (line && latlon.length > 0) {{
        map.removeLayer(line);
        const newLineColor = isDarkNow ? '#4db6ff' : '#0078ff';
        line = L.polyline(latlon, {{color: newLineColor, weight: 5, opacity: 0.8}}).addTo(map);
        
        // Make sure markers stay on top
        if (startMarker) startMarker.addTo(map);
        if (endMarker) endMarker.addTo(map);
      }}
    }} catch (e) {{
      console.error("Error updating map style:", e);
    }}
  }}
}} catch (error) {{
  console.error("Error initializing map:", error);
  document.getElementById('map').innerHTML = '<div style="padding: 20px; text-align: center;">' + 
    '<p>Error loading map: ' + error.message + '</p>' +
    '<p>Please check your internet connection and try again.</p>' +
    '<button onclick="location.reload()">Reload Page</button>' +
    '</div>';
}}
</script>
</body></html>
"""
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(html)
    return outfile

# --- GUI ---
def main():
    root = tk.Tk()
    root.title("Graphhopper Route → Report (PH defaults)")
    root.resizable(False, False)

    frm = ttk.Frame(root, padding=10)
    frm.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frm, text="Origin:").grid(row=0, column=0, sticky="w", pady=4)
    e_origin = ttk.Entry(frm, width=50)
    e_origin.grid(row=0, column=1, pady=4)

    ttk.Label(frm, text="Destination:").grid(row=1, column=0, sticky="w", pady=4)
    e_dest = ttk.Entry(frm, width=50)
    e_dest.grid(row=1, column=1, pady=4)

    ttk.Label(frm, text="Vehicle:").grid(row=2, column=0, sticky="w", pady=4)
    vehicle_var = tk.StringVar(value="car")
    vehicle_choices = ["car", "bike", "foot", "motorcycle", "truck", "ebike", "scooter"]
    cmb = ttk.Combobox(frm, textvariable=vehicle_var, values=vehicle_choices, state="readonly", width=12)
    cmb.grid(row=2, column=1, sticky="w", pady=4)

    status_var = tk.StringVar(value="Ready")
    ttk.Label(frm, textvariable=status_var, foreground="#0b6").grid(row=7, column=0, columnspan=2, pady=4, sticky="w")


    def on_generate():
        o, d = e_origin.get().strip(), e_dest.get().strip()
        v = vehicle_var.get()
        if not o or not d:
            messagebox.showwarning("Missing Input", "Please fill in both Origin and Destination.")
            return
        options = {
            "fuel_eff_l100": DEFAULT_FUEL_EFF_L100,
            "fuel_price_per_l": DEFAULT_GASOLINE_PHP_PER_L,
            "fuel_price_overridden": None,
            "dark_mode": False,  # Default to light mode, user can toggle in the report
        }
        # open loading modal and start thread
        loading_modal, pb = open_loading_modal(root, title="Generating report — please wait")
        # pass the modal to the thread so it can close it when done
        t = threading.Thread(target=run_route_threaded, args=(root, o, d, v, status_var, options, loading_modal), daemon=True)
        t.start()

    ttk.Button(frm, text="Generate Report", command=on_generate).grid(row=8, column=0, columnspan=2, sticky="ew", pady=8)
    e_origin.focus()
    root.mainloop()

if __name__ == "__main__":
    main()
