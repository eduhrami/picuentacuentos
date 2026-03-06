#!/bin/bash
#
# RP4 Kids Audio Player - Installation Script
# For Raspberry Pi OS (64-bit) on RaspberryPi 4
# Version: 1.0
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="/home/pi/rp4player"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Print colored message
print_msg() {
    echo -e "${GREEN}[RP4Player]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}==>${NC} ${GREEN}$1${NC}"
}

# Check if running on Raspberry Pi
check_platform() {
    print_step "Checking platform..."

    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        print_warning "This doesn't appear to be a Raspberry Pi"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Check architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "aarch64" ]]; then
        print_msg "Detected 64-bit ARM architecture ✓"
    elif [[ "$ARCH" == "armv7l" ]]; then
        print_msg "Detected 32-bit ARM architecture ✓"
    else
        print_warning "Unknown architecture: $ARCH"
    fi
}

# Check if running as correct user
check_user() {
    if [[ "$EUID" -eq 0 ]]; then
        print_error "Please run as pi user, not root"
        print_msg "Usage: ./setup.sh"
        exit 1
    fi
}

# Update system packages
update_system() {
    print_step "Updating system packages..."
    sudo apt-get update
    print_msg "System package list updated"
}

# Install system dependencies
install_dependencies() {
    print_step "Installing system dependencies..."

    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-setuptools \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
        libportmidi-dev \
        libswscale-dev \
        libavformat-dev \
        libavcodec-dev \
        libjpeg-dev \
        libtiff5-dev \
        libfreetype6-dev \
        libffi-dev \
        libssl-dev \
        libasound2-dev \
        alsa-utils \
        git \
        vim \
        htop

    print_msg "System dependencies installed ✓"
}

# Configure audio output to 3.5mm jack
configure_audio() {
    print_step "Configuring audio output for 3.5mm jack..."

    # Backup config.txt
    sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup 2>/dev/null || \
    sudo cp /boot/config.txt /boot/config.txt.backup 2>/dev/null || true

    # Determine config file location
    if [ -f /boot/firmware/config.txt ]; then
        CONFIG_FILE="/boot/firmware/config.txt"
    else
        CONFIG_FILE="/boot/config.txt"
    fi

    # Add audio configuration if not present
    if ! grep -q "dtparam=audio=on" "$CONFIG_FILE"; then
        print_msg "Adding audio configuration to $CONFIG_FILE"
        sudo tee -a "$CONFIG_FILE" > /dev/null <<EOF

# RP4 Player Audio Configuration
dtparam=audio=on
audio_pwm_mode=2
disable_audio_dither=1
EOF
    else
        print_msg "Audio already configured in $CONFIG_FILE"
    fi

    # Force analog output
    print_msg "Setting audio output to 3.5mm jack..."
    amixer cset numid=3 1 2>/dev/null || print_warning "Could not set audio output (will configure after reboot)"

    print_msg "Audio configuration complete ✓"
}

# Create directory structure
create_directories() {
    print_step "Creating directory structure..."

    # Use installation directory
    cd "$INSTALL_DIR"

    # Create directory structure
    mkdir -p data/backups
    mkdir -p config
    mkdir -p media/alarms
    mkdir -p media/stories
    mkdir -p logs
    mkdir -p assets/fonts
    mkdir -p assets/icons
    mkdir -p assets/kv

    print_msg "Directory structure created ✓"
}

# Set up Python virtual environment
setup_python_env() {
    print_step "Setting up Python virtual environment..."

    cd "$INSTALL_DIR"

    # Create virtual environment
    python3 -m venv venv

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    print_msg "Virtual environment created ✓"
}

# Install Python packages
install_python_packages() {
    print_step "Installing Python packages..."

    cd "$INSTALL_DIR"
    source venv/bin/activate

    # Install from requirements.txt if exists
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found, installing packages manually..."

        # Install packages one by one for better error handling
        pip install Cython==0.29.36
        pip install kivy==2.2.1
        pip install pygame==2.5.2
        pip install APScheduler==3.10.4
        pip install pyudev==0.24.1
        pip install mutagen==1.47.0
        pip install python-dateutil==2.8.2
    fi

    print_msg "Python packages installed ✓"
}

# Initialize data files
initialize_data() {
    print_step "Initializing data files..."

    cd "$INSTALL_DIR"

    # Create default settings.json
    cat > config/settings.json <<'EOF'
{
  "audio": {
    "output_device": "hw:0,0",
    "default_volume": 0.7,
    "alarm_volume": 0.8,
    "max_volume": 0.85
  },
  "display": {
    "brightness": 80,
    "auto_dim_timeout": 30,
    "dim_brightness": 20,
    "orientation": 0
  },
  "alarms": {
    "snooze_duration_minutes": 5,
    "auto_dismiss_minutes": 10,
    "max_alarms": 5
  },
  "stories": {
    "default_sleep_timer_minutes": 30,
    "resume_playback": true
  },
  "usb": {
    "auto_sync": true,
    "media_path": "/home/pi/rp4player/media"
  },
  "system": {
    "log_level": "INFO",
    "log_file": "/home/pi/rp4player/logs/app.log"
  }
}
EOF

    # Create empty alarms.json
    cat > data/alarms.json <<'EOF'
{
  "alarms": [],
  "next_id": 1
}
EOF

    # Create empty media.json
    cat > data/media.json <<'EOF'
{
  "media_files": [],
  "next_id": 1
}
EOF

    # Create empty playback.json
    cat > data/playback.json <<'EOF'
{
  "current_media_id": null,
  "position_seconds": 0.0,
  "volume": 0.7,
  "is_playing": false,
  "sleep_timer_enabled": false,
  "sleep_timer_end_time": null,
  "playlist": [],
  "playlist_index": 0,
  "last_updated": null
}
EOF

    print_msg "Data files initialized ✓"
}

# Copy sample media files
setup_sample_media() {
    print_step "Setting up sample media..."

    # Create sample alarm sound (if not exists)
    if [ ! -f "$INSTALL_DIR/media/alarms/sample-alarm.txt" ]; then
        cat > "$INSTALL_DIR/media/alarms/README.txt" <<'EOF'
Place your alarm sound MP3 files in this directory.

Recommended format:
- File format: MP3
- Length: 15-60 seconds
- Bitrate: 128kbps or higher
- Sample rate: 44.1kHz

Example files:
- rooster.mp3
- gentle-bells.mp3
- birds-chirping.mp3
EOF
    fi

    # Create sample story readme
    if [ ! -f "$INSTALL_DIR/media/stories/README.txt" ]; then
        cat > "$INSTALL_DIR/media/stories/README.txt" <<'EOF'
Place your bedtime story MP3 files in this directory.

Recommended format:
- File format: MP3
- Length: 5-30 minutes
- Bitrate: 128kbps
- Sample rate: 44.1kHz

Example files:
- three-little-pigs.mp3
- goldilocks.mp3
- little-red-riding-hood.mp3

You can add ID3 tags for better display:
- Title: Story name
- Artist: Narrator name
- Album: Story collection
EOF
    fi

    print_msg "Sample media setup complete ✓"
}

# Create systemd service
create_systemd_service() {
    print_step "Creating systemd service..."

    sudo tee /etc/systemd/system/rp4player.service > /dev/null <<EOF
[Unit]
Description=RP4 Kids Audio Player
After=sound.target network.target graphical.target
Wants=graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=$INSTALL_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
ExecStartPre=/bin/sleep 5
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/app/main.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/service.log
StandardError=append:$INSTALL_DIR/logs/service-error.log

[Install]
WantedBy=graphical.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload

    print_msg "Systemd service created ✓"
}

# Configure autostart (alternative to systemd)
configure_autostart() {
    print_step "Configuring autostart..."

    # Create autostart directory
    mkdir -p /home/pi/.config/autostart

    # Create desktop entry
    cat > /home/pi/.config/autostart/rp4player.desktop <<EOF
[Desktop Entry]
Type=Application
Name=RP4 Kids Player
Comment=Kids Audio Player and Alarm Clock
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/app/main.py
Terminal=false
StartupNotify=false
EOF

    chmod +x /home/pi/.config/autostart/rp4player.desktop

    print_msg "Autostart configured ✓"
}

# Disable screen blanking
disable_screen_blanking() {
    print_step "Disabling screen blanking..."

    # Create/edit LXDE autostart
    mkdir -p /home/pi/.config/lxsession/LXDE-pi

    if [ ! -f /home/pi/.config/lxsession/LXDE-pi/autostart ]; then
        cp /etc/xdg/lxsession/LXDE-pi/autostart /home/pi/.config/lxsession/LXDE-pi/autostart 2>/dev/null || true
    fi

    # Add screen blanking disable commands
    cat >> /home/pi/.config/lxsession/LXDE-pi/autostart <<'EOF'

# Disable screen blanking for RP4 Player
@xset s off
@xset -dpms
@xset s noblank
EOF

    print_msg "Screen blanking disabled ✓"
}

# Test audio
test_audio() {
    print_step "Testing audio output..."

    if [ -f /usr/share/sounds/alsa/Front_Center.wav ]; then
        print_msg "Playing test sound..."
        aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null || print_warning "Could not play test sound"
    else
        print_warning "Test sound file not found, skipping audio test"
    fi
}

# Set permissions
set_permissions() {
    print_step "Setting permissions..."

    cd "$INSTALL_DIR"

    # Make scripts executable
    find . -name "*.sh" -type f -exec chmod +x {} \;

    # Set ownership
    sudo chown -R pi:pi "$INSTALL_DIR"

    # Make main.py executable
    if [ -f app/main.py ]; then
        chmod +x app/main.py
    fi

    print_msg "Permissions set ✓"
}

# Create helper scripts
create_helper_scripts() {
    print_step "Creating helper scripts..."

    # Create start script
    cat > "$INSTALL_DIR/start.sh" <<'EOF'
#!/bin/bash
cd /home/pi/rp4player
source venv/bin/activate
python app/main.py
EOF
    chmod +x "$INSTALL_DIR/start.sh"

    # Create stop script
    cat > "$INSTALL_DIR/stop.sh" <<'EOF'
#!/bin/bash
pkill -f "python.*rp4player"
sudo systemctl stop rp4player
EOF
    chmod +x "$INSTALL_DIR/stop.sh"

    # Create update script
    cat > "$INSTALL_DIR/update.sh" <<'EOF'
#!/bin/bash
cd /home/pi/rp4player
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart rp4player
EOF
    chmod +x "$INSTALL_DIR/update.sh"

    # Create backup script
    cat > "$INSTALL_DIR/backup.sh" <<'EOF'
#!/bin/bash
BACKUP_DIR="/home/pi/rp4player/data/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

# Backup data files
cp data/alarms.json "$BACKUP_DIR/alarms_${TIMESTAMP}.json"
cp data/media.json "$BACKUP_DIR/media_${TIMESTAMP}.json"
cp data/playback.json "$BACKUP_DIR/playback_${TIMESTAMP}.json"
cp config/settings.json "$BACKUP_DIR/settings_${TIMESTAMP}.json"

echo "Backup created: $TIMESTAMP"

# Keep only last 10 backups
cd "$BACKUP_DIR"
ls -t | tail -n +41 | xargs -r rm

echo "Old backups cleaned up"
EOF
    chmod +x "$INSTALL_DIR/backup.sh"

    print_msg "Helper scripts created ✓"
}

# Print installation summary
print_summary() {
    echo
    print_step "Installation Summary"
    echo
    print_msg "✓ RP4 Kids Audio Player installed successfully!"
    echo
    echo -e "${BLUE}Installation Directory:${NC} $INSTALL_DIR"
    echo -e "${BLUE}Python Version:${NC} $(python3 --version)"
    echo -e "${BLUE}Architecture:${NC} $(uname -m)"
    echo
    echo -e "${GREEN}Next Steps:${NC}"
    echo
    echo "1. Add MP3 files to:"
    echo "   - Alarms:  $INSTALL_DIR/media/alarms/"
    echo "   - Stories: $INSTALL_DIR/media/stories/"
    echo
    echo "2. Test the application:"
    echo "   cd $INSTALL_DIR"
    echo "   ./start.sh"
    echo
    echo "3. Enable auto-start on boot:"
    echo "   sudo systemctl enable rp4player"
    echo "   sudo systemctl start rp4player"
    echo
    echo "4. View logs:"
    echo "   tail -f $INSTALL_DIR/logs/app.log"
    echo
    echo "5. Reboot to apply all changes:"
    echo "   sudo reboot"
    echo
    echo -e "${YELLOW}Helper Scripts:${NC}"
    echo "   ./start.sh   - Start the application"
    echo "   ./stop.sh    - Stop the application"
    echo "   ./backup.sh  - Backup configuration"
    echo "   ./update.sh  - Update application"
    echo
    echo -e "${YELLOW}Service Management:${NC}"
    echo "   sudo systemctl status rp4player   - Check status"
    echo "   sudo systemctl restart rp4player  - Restart"
    echo "   sudo systemctl stop rp4player     - Stop"
    echo
}

# Main installation flow
main() {
    clear
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════╗"
    echo "║  RP4 Kids Audio Player - Setup Script     ║"
    echo "║  Version 1.0                               ║"
    echo "║  For Raspberry Pi OS (64-bit)              ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${NC}"

    check_user
    check_platform

    print_warning "This script will install RP4 Player to: $INSTALL_DIR"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_msg "Installation cancelled"
        exit 0
    fi

    # Copy files to installation directory if not already there
    if [ "$PROJECT_DIR" != "$INSTALL_DIR" ]; then
        print_step "Copying files to $INSTALL_DIR..."
        mkdir -p "$INSTALL_DIR"
        rsync -av --exclude='venv' --exclude='.git' --exclude='*.pyc' \
              "$PROJECT_DIR/" "$INSTALL_DIR/"
        print_msg "Files copied ✓"
    fi

    update_system
    install_dependencies
    configure_audio
    create_directories
    setup_python_env
    install_python_packages
    initialize_data
    setup_sample_media
    set_permissions
    create_helper_scripts
    create_systemd_service
    configure_autostart
    disable_screen_blanking

    print_summary

    print_msg "Setup complete! 🎉"
    echo
    print_warning "A reboot is recommended to apply all changes"
    read -p "Reboot now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    fi
}

# Run main installation
main "$@"
