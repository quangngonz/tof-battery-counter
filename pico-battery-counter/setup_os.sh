#!/bin/bash
# ============================================================================
# Battery Counter - OS Setup Script
# ============================================================================
# This script installs all system dependencies and Python packages required
# for the Raspberry Pi Battery Counter project.
#
# Usage: ./setup_os.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    print_header "Checking System Compatibility"
    
    if [ ! -f /proc/device-tree/model ]; then
        print_error "This doesn't appear to be a Raspberry Pi!"
        print_warning "Continuing anyway, but hardware features may not work."
    else
        MODEL=$(cat /proc/device-tree/model)
        print_success "Detected: $MODEL"
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    print_info "Architecture: $ARCH"
    
    if [[ "$ARCH" != "armv7l" && "$ARCH" != "armv6l" && "$ARCH" != "aarch64" ]]; then
        print_warning "This script is designed for Raspberry Pi OS (32-bit or 64-bit)"
        print_warning "Detected: $ARCH - This may not be compatible"
    else
        if [[ "$ARCH" == "aarch64" ]]; then
            print_success "64-bit Raspberry Pi OS detected"
        else
            print_success "32-bit Raspberry Pi OS detected"
        fi
    fi
}

# Update system
update_system() {
    print_header "Updating System Packages"
    
    print_info "Running apt update..."
    sudo apt update
    print_success "Package lists updated"
    
    print_info "Running apt upgrade (this may take a while)..."
    sudo apt upgrade -y
    print_success "System packages upgraded"
}

# Enable I2C and SPI interfaces
enable_interfaces() {
    print_header "Enabling I2C and SPI Interfaces"
    
    # Check if raspi-config is available
    if ! command -v raspi-config &> /dev/null; then
        print_error "raspi-config not found! Cannot enable interfaces automatically."
        print_warning "Please enable I2C and SPI manually using: sudo raspi-config"
        return 1
    fi
    
    # Enable I2C
    print_info "Enabling I2C..."
    sudo raspi-config nonint do_i2c 0
    print_success "I2C enabled"
    
    # Enable SPI
    print_info "Enabling SPI..."
    sudo raspi-config nonint do_spi 0
    print_success "SPI enabled"
    
    print_warning "A reboot will be required after installation completes"
}

# Install system dependencies
install_system_packages() {
    print_header "Installing System Dependencies"
    
    PACKAGES=(
        "python3"
        "python3-pip"
        "python3-dev"
        "python3-pil"
        "i2c-tools"
        "git"
        "libjpeg-dev"
        "zlib1g-dev"
        "libfreetype6-dev"
        "rpi.gpio-common"
    )
    
    print_info "Installing: ${PACKAGES[*]}"
    sudo apt install -y "${PACKAGES[@]}"
    print_success "System packages installed"
}

# Install Python dependencies
install_python_packages() {
    print_header "Installing Python Dependencies"
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    sudo pip3 install --upgrade pip
    print_success "pip upgraded"
    
    # Install Python packages
    PYTHON_PACKAGES=(
        "RPi.GPIO"
        "spidev"
        "smbus2"
        "Pillow"
        "requests"
    )
    
    for package in "${PYTHON_PACKAGES[@]}"; do
        print_info "Installing $package..."
        sudo pip3 install "$package"
        print_success "$package installed"
    done
}

# Add user to required groups
setup_user_permissions() {
    print_header "Setting Up User Permissions"
    
    CURRENT_USER=$(whoami)
    
    # Add user to i2c group
    if getent group i2c > /dev/null 2>&1; then
        print_info "Adding $CURRENT_USER to i2c group..."
        sudo usermod -a -G i2c "$CURRENT_USER"
        print_success "Added to i2c group"
    else
        print_warning "i2c group not found, skipping..."
    fi
    
    # Add user to gpio group
    if getent group gpio > /dev/null 2>&1; then
        print_info "Adding $CURRENT_USER to gpio group..."
        sudo usermod -a -G gpio "$CURRENT_USER"
        print_success "Added to gpio group"
    else
        print_warning "gpio group not found, skipping..."
    fi
    
    # Add user to spi group
    if getent group spi > /dev/null 2>&1; then
        print_info "Adding $CURRENT_USER to spi group..."
        sudo usermod -a -G spi "$CURRENT_USER"
        print_success "Added to spi group"
    else
        print_warning "spi group not found, skipping..."
    fi
    
    print_warning "You may need to log out and log back in for group changes to take effect"
}

# Verify installations
verify_installation() {
    print_header "Verifying Installation"
    
    # Check Python version
    print_info "Checking Python version..."
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION"
    
    # Check pip version
    print_info "Checking pip version..."
    PIP_VERSION=$(pip3 --version)
    print_success "$PIP_VERSION"
    
    # Verify Python packages
    print_info "Verifying Python packages..."
    VERIFY_PACKAGES=("RPi.GPIO" "spidev" "smbus2" "PIL" "requests")
    
    for package in "${VERIFY_PACKAGES[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_success "$package is installed"
        else
            print_error "$package is NOT installed!"
        fi
    done
    
    # Check I2C tools
    print_info "Checking I2C tools..."
    if command -v i2cdetect &> /dev/null; then
        print_success "i2c-tools installed"
    else
        print_error "i2c-tools NOT found!"
    fi
    
    # Check SPI devices
    print_info "Checking SPI devices..."
    if [ -e /dev/spidev0.0 ]; then
        print_success "SPI devices found: $(ls /dev/spidev*)"
    else
        print_warning "SPI devices not found (may require reboot)"
    fi
    
    # Check I2C devices
    print_info "Checking I2C devices..."
    if [ -e /dev/i2c-1 ]; then
        print_success "I2C devices found: $(ls /dev/i2c*)"
    else
        print_warning "I2C devices not found (may require reboot)"
    fi
}

# Create requirements.txt for future reference
create_requirements_file() {
    print_header "Creating requirements.txt"
    
    REQUIREMENTS_FILE="requirements.txt"
    
    cat > "$REQUIREMENTS_FILE" << EOF
# Python dependencies for Battery Counter
# Install with: sudo pip3 install -r requirements.txt

RPi.GPIO>=0.7.0
spidev>=3.5
smbus2>=0.4.0
Pillow>=8.0.0
requests>=2.25.0
EOF
    
    print_success "Created $REQUIREMENTS_FILE"
}

# Main installation flow
main() {
    print_header "Battery Counter - OS Setup Script"
    print_info "This script will install all required dependencies"
    print_warning "This script requires sudo privileges"
    echo ""
    
    # Ask for confirmation
    read -p "Continue with installation? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Installation cancelled"
        exit 1
    fi
    
    # Run installation steps
    check_raspberry_pi
    update_system
    enable_interfaces
    install_system_packages
    install_python_packages
    setup_user_permissions
    create_requirements_file
    verify_installation
    
    # Final message
    print_header "Installation Complete!"
    print_success "All dependencies have been installed"
    echo ""
    print_info "Next steps:"
    echo "  1. Reboot your Raspberry Pi: sudo reboot"
    echo "  2. After reboot, verify I2C sensor: sudo i2cdetect -y 1"
    echo "  3. Configure config.py with your settings"
    echo "  4. Test the application: python3 main.py"
    echo "  5. Set up as service: ./setup_service.sh"
    echo ""
    print_warning "IMPORTANT: A reboot is required for I2C and SPI to work properly!"
    echo ""
    
    # Ask if user wants to reboot now
    read -p "Reboot now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Rebooting in 5 seconds... (Ctrl+C to cancel)"
        sleep 5
        sudo reboot
    else
        print_warning "Remember to reboot before running the application!"
    fi
}

# Run main function
main
