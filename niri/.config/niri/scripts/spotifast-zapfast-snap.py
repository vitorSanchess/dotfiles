#!/usr/bin/env python3
import json
import subprocess
import time
import sys
import os

SETTINGS_PATH = os.path.expanduser("~/.config/spotifast/settings.json")

def get_windows():
    try:
        out = subprocess.check_output(["niri", "msg", "-j", "windows"], text=True)
        return json.loads(out)
    except Exception:
        return []

def run_action(*args):
    subprocess.run(["niri", "msg", "action", *args], check=False)

def is_spotifast_mini(spot):
    # Method 1: Check actual window geometry in Niri
    spot_layout = spot.get("layout", {})
    spot_size = spot_layout.get("window_size", [0, 0])
    spot_h = spot_size[1]
    if 0 < spot_h <= 300:
        return True

    # Method 2: Check Spotifast's settings.json
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                settings = json.load(f)
                if settings.get("winamp_window", False):
                    return True
    except Exception:
        pass

    return False

def snap_spotifast():
    windows = get_windows()
    spot = next((w for w in windows if w.get("app_id") == "spotifast"), None)
    zap = next((w for w in windows if w.get("app_id") == "zapfast"), None)

    if not spot or not zap:
        return

    is_mini = is_spotifast_mini(spot)

    spot_id = spot["id"]
    zap_id = zap["id"]
    zap_ws = zap["workspace_id"]
    spot_ws = spot["workspace_id"]

    spot_pos = spot.get("layout", {}).get("pos_in_scrolling_layout", [0, 0])  # [col, row]
    zap_pos = zap.get("layout", {}).get("pos_in_scrolling_layout", [0, 0])

    focused = next((w for w in windows if w.get("is_focused")), None)
    focused_id = focused["id"] if focused else None

    if is_mini:
        # Already snapped: same workspace, same column, spotifast row 1, zapfast row 2
        if spot_ws == zap_ws and spot_pos[0] == zap_pos[0] and spot_pos[1] == 1 and zap_pos[1] == 2:
            return

        # 1. Move to same workspace if needed
        if spot_ws != zap_ws:
            run_action("move-window-to-workspace", "--window-id", str(spot_id), "--focus", "false", str(zap_ws))
            time.sleep(0.05)

        # 2. If in a different column, move spotifast next to zapfast and consume
        if spot_pos[0] != zap_pos[0]:
            run_action("focus-window", "--id", str(spot_id))
            run_action("move-column-to-index", str(zap_pos[0] + 1))
            run_action("consume-or-expel-window-left", "--id", str(spot_id))
            time.sleep(0.05)

        # 3. Ensure spotifast is on top of zapfast (row 1)
        windows = get_windows()
        spot = next((w for w in windows if w.get("id") == spot_id), None)
        if spot:
            s_row = spot.get("layout", {}).get("pos_in_scrolling_layout", [0, 0])[1]
            if s_row > 1:
                run_action("focus-window", "--id", str(spot_id))
                run_action("move-window-up")

        # 4. Set height and column width
        run_action("focus-window", "--id", str(spot_id))
        run_action("set-window-height", "--id", str(spot_id), "180")
        run_action("set-column-width", "460")

        # 5. Restore focus
        if focused_id and focused_id != spot_id:
            run_action("focus-window", "--id", str(focused_id))

    else:
        # Full player: expel from zapfast's column if currently stacked with it
        if spot_ws == zap_ws and spot_pos[0] == zap_pos[0]:
            run_action("focus-window", "--id", str(spot_id))
            run_action("consume-or-expel-window-right", "--id", str(spot_id))
            run_action("reset-window-height", "--id", str(spot_id))
            if focused_id and focused_id != spot_id:
                run_action("focus-window", "--id", str(focused_id))

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        snap_spotifast()
        return

    # Daemon mode: listen to niri event stream
    proc = subprocess.Popen(["niri", "msg", "-j", "event-stream"], stdout=subprocess.PIPE, text=True)
    last_check = 0.0

    while True:
        line = proc.stdout.readline()
        if not line:
            break
        
        # Debounce: avoid running multiple times in rapid bursts (< 0.2s)
        now = time.time()
        if "WindowOpenedOrChanged" in line or "WindowsChanged" in line:
            if now - last_check > 0.25:
                last_check = now
                snap_spotifast()

if __name__ == "__main__":
    main()
