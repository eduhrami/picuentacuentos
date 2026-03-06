# ============================================================
# AUTO-START X SERVER ON tty1 - Kiosk mode
# This file runs when user pi logs in on the console.
# X will be restarted automatically if it crashes.
# ============================================================

# Tell X which framebuffer device to use (LCD = /dev/fb1)
export FRAMEBUFFER=/dev/fb1

# Only start X on tty1 (the main console), and only if not
# already inside an X session (DISPLAY is empty).
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    echo "Starting X server on LCD (fb1)..."
    # Loop: restart X automatically if it exits or crashes
    while true; do
        startx -- :0 vt1 -nolisten tcp 2>&1 | tee /tmp/x_startup.log
        echo "X server exited, restarting in 3 seconds..." >&2
        sleep 3
    done
fi
