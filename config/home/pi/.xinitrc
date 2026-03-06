#!/bin/bash
# ============================================================
# X SESSION CONFIGURATION - Kiosk mode for 3.5" LCD (480x320)
# This file is executed by startx when the X server starts.
# Do NOT change the app to launch here — edit ~/kiosk.conf
# ============================================================

# --- Screen saver / power management: disable all blanking ---
xset s off       # Disable screen saver
xset -dpms       # Disable Display Power Management Signaling
xset s noblank   # Prevent framebuffer blanking

# --- Load the kiosk app setting from the config file ---
# Edit ~/kiosk.conf to change which app runs.
KIOSK_CONF="$HOME/kiosk.conf"
if [ -f "$KIOSK_CONF" ]; then
    # shellcheck source=/dev/null
    source "$KIOSK_CONF"
else
    echo "WARNING: $KIOSK_CONF not found, falling back to xeyes" >&2
    KIOSK_APP="xeyes -geometry 480x320+0+0"
    KIOSK_DISPLAY=":0"
fi

# --- Export the display so the app can connect to X ---
export DISPLAY="${KIOSK_DISPLAY}"

# --- Kiosk loop: launch the app, restart it if it crashes ---
# This keeps the display alive even if the app exits unexpectedly.
while true; do
    $KIOSK_APP
    sleep 1   # Brief pause before restart to avoid tight crash loop
done
