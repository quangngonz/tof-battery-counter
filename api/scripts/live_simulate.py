import os
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError(
        "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment variables")
supabase: Client = create_client(supabase_url, supabase_key)

# Device configurations
DEVICE_CONFIGS = {
    'picos': [
        {'id': 'pico-001', 'location': 'Building A - Floor 1', 'activity': 0.7},
        {'id': 'pico-002', 'location': 'Building A - Floor 2', 'activity': 0.6},
        {'id': 'pico-003', 'location': 'Building B - Floor 1', 'activity': 0.8},
        {'id': 'pico-004', 'location': 'Building B - Floor 2', 'activity': 0.5},
        {'id': 'pico-005', 'location': 'Building C - Main Entrance', 'activity': 0.9},
    ],
    'pis': [
        {'id': 'pi-zero-001', 'location': 'Storage Room A', 'activity': 0.4},
        {'id': 'pi-zero-002', 'location': 'Storage Room B', 'activity': 0.3},
        {'id': 'pi-4-001', 'location': 'Main Office', 'activity': 0.7},
        {'id': 'pi-4-002', 'location': 'Workshop', 'activity': 0.6},
    ]
}


def get_all_devices():
    """Get a flat list of all devices"""
    return DEVICE_CONFIGS['picos'] + DEVICE_CONFIGS['pis']


def generate_random_entry(device):
    """
    Generate a random battery log entry for a device

    Args:
        device: Device configuration dictionary

    Returns:
        Dictionary with timestamp, amount, and device_id
    """
    device_id = device['id']
    device_type = 'pico' if device_id.startswith('pico') else 'pi'

    # Different amount ranges based on device type
    if device_type == 'pico':
        # Picos: smaller collections (1-3 typically, rarely up to 5)
        if random.random() < 0.85:
            amount = random.randint(1, 3)
        else:
            amount = random.randint(4, 5)
    else:  # pi
        # Raspberry Pis: larger collections (2-5 typically, rarely up to 10)
        if random.random() < 0.85:
            amount = random.randint(2, 5)
        else:
            amount = random.randint(6, 10)

    return {
        'timestamp': datetime.now().isoformat(),
        'amount': amount,
        'device_id': device_id
    }


def insert_entry(entry):
    """
    Insert a single entry into the database

    Args:
        entry: Dictionary with timestamp, amount, and device_id

    Returns:
        True if successful, False otherwise
    """
    try:
        supabase.table('battery_logs').insert(entry).execute()
        return True
    except Exception as e:
        print(f"❌ Error inserting entry: {str(e)}")
        return False


def run_simulation(tick_interval=5, activity_multiplier=1.0, specific_devices=None):
    """
    Run live simulation that adds random entries every tick

    Args:
        tick_interval: Seconds between each tick (default: 5)
        activity_multiplier: Multiplier for device activity rates (default: 1.0)
        specific_devices: List of specific device IDs to simulate (None = all devices)
    """
    # Get devices to simulate
    all_devices = get_all_devices()

    if specific_devices:
        devices = [d for d in all_devices if d['id'] in specific_devices]
        if not devices:
            print(
                f"❌ No matching devices found for: {', '.join(specific_devices)}")
            return
    else:
        devices = all_devices

    print("🔋 Battery Logger Live Simulator")
    print("=" * 60)
    print(f"⏱️  Tick interval: {tick_interval} seconds")
    print(f"📊 Activity multiplier: {activity_multiplier}x")
    print(f"📱 Simulating {len(devices)} devices:")
    for device in devices:
        activity_rate = device['activity'] * activity_multiplier * 100
        print(
            f"   • {device['id']:<15} - {device['location']:<30} ({activity_rate:.0f}% active)")
    print("=" * 60)
    print("\n🚀 Starting simulation... (Press Ctrl+C to stop)\n")

    tick_count = 0
    total_entries = 0

    try:
        while True:
            tick_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            entries_this_tick = []

            # Each device has a chance to generate an entry based on its activity rate
            for device in devices:
                # Apply activity multiplier to device's base activity rate
                effective_activity = min(
                    device['activity'] * activity_multiplier, 1.0)

                # Random chance based on device's activity rate
                if random.random() < effective_activity:
                    entry = generate_random_entry(device)
                    entries_this_tick.append(entry)

            # Insert all entries from this tick
            successful_inserts = 0
            for entry in entries_this_tick:
                if insert_entry(entry):
                    successful_inserts += 1
                    total_entries += 1
                    device_id = entry['device_id']
                    amount = entry['amount']
                    print(
                        f"✅ [{current_time}] {device_id}: +{amount} batteries")

            if len(entries_this_tick) == 0:
                print(f"⏸️  [{current_time}] Tick #{tick_count}: No activity")
            elif successful_inserts > 0:
                print(
                    f"📊 Tick #{tick_count}: {successful_inserts} entries added (Total: {total_entries})")

            # Wait for next tick
            time.sleep(tick_interval)

    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("🛑 Simulation stopped by user")
        print(f"📊 Summary:")
        print(f"   • Total ticks: {tick_count}")
        print(f"   • Total entries added: {total_entries}")
        print(f"   • Average entries per tick: {total_entries/tick_count:.2f}")
        print(f"   • Runtime: {tick_count * tick_interval} seconds")
        print("=" * 60)


def print_help():
    """Print help message"""
    help_text = """
Battery Logger Live Simulator

Continuously simulates battery log entries being added in real-time.
Each "tick" represents a time interval where devices may report battery collections.

Usage:
    python live_simulate.py [OPTIONS]

Options:
    -h, --help              Show this help message
    --tick N               Seconds between each simulation tick (default: 5)
    --activity N           Activity multiplier (0.1-5.0) (default: 1.0)
                          Higher values = more frequent entries
    --devices ID1,ID2,...  Simulate only specific device IDs (comma-separated)
    --list                 List all available devices and exit

Examples:
    python live_simulate.py
        Run simulation with default settings (5 second ticks, normal activity)

    python live_simulate.py --tick 2
        Run with 2 second intervals between ticks

    python live_simulate.py --activity 2.0
        Run with 2x normal activity (more entries)

    python live_simulate.py --activity 0.5
        Run with 50% activity (fewer entries)

    python live_simulate.py --tick 1 --activity 1.5
        Fast ticks (1 sec) with increased activity

    python live_simulate.py --devices pico-001,pico-002
        Simulate only pico-001 and pico-002

    python live_simulate.py --devices pi-4-001 --tick 3 --activity 2.0
        Simulate only pi-4-001 with 3 second ticks and double activity

Activity Rates:
    Each device has a base activity rate (probability of generating an entry per tick):
    - High traffic locations: 70-90% 
    - Medium traffic: 50-70%
    - Low traffic: 30-50%
    
    The --activity multiplier scales these rates up or down.

Tips:
    - Use lower tick intervals (1-2 sec) for faster testing
    - Use higher activity multipliers (2-3x) to generate more data quickly
    - Use specific devices to focus on particular locations
    - Press Ctrl+C to stop the simulation and see statistics
"""
    print(help_text)


def print_device_list():
    """Print list of all available devices with their activity rates"""
    print("\n📱 Available Devices:\n")
    print("Raspberry Pi Picos:")
    for device in DEVICE_CONFIGS['picos']:
        activity_pct = device['activity'] * 100
        print(
            f"  • {device['id']:<15} - {device['location']:<30} ({activity_pct:.0f}% activity)")

    print("\nRaspberry Pis:")
    for device in DEVICE_CONFIGS['pis']:
        activity_pct = device['activity'] * 100
        print(
            f"  • {device['id']:<15} - {device['location']:<30} ({activity_pct:.0f}% activity)")
    print()


def main():
    """Main execution function"""
    try:
        import sys

        # Check for help flag
        if '-h' in sys.argv or '--help' in sys.argv:
            print_help()
            return 0

        # Check for list flag
        if '--list' in sys.argv:
            print_device_list()
            return 0

        # Parse --tick argument
        tick_interval = 5
        if '--tick' in sys.argv:
            try:
                tick_index = sys.argv.index('--tick')
                tick_interval = float(sys.argv[tick_index + 1])
                if tick_interval <= 0:
                    print("❌ Error: --tick must be a positive number")
                    return 1
            except (IndexError, ValueError):
                print("❌ Error: --tick requires a valid number argument")
                return 1

        # Parse --activity argument
        activity_multiplier = 1.0
        if '--activity' in sys.argv:
            try:
                activity_index = sys.argv.index('--activity')
                activity_multiplier = float(sys.argv[activity_index + 1])
                if activity_multiplier <= 0 or activity_multiplier > 5.0:
                    print("❌ Error: --activity must be between 0.1 and 5.0")
                    return 1
            except (IndexError, ValueError):
                print("❌ Error: --activity requires a valid number argument")
                return 1

        # Parse --devices argument
        specific_devices = None
        if '--devices' in sys.argv:
            try:
                devices_index = sys.argv.index('--devices')
                devices_str = sys.argv[devices_index + 1]
                specific_devices = [d.strip() for d in devices_str.split(',')]
            except IndexError:
                print("❌ Error: --devices requires comma-separated device IDs")
                return 1

        # Run the simulation
        run_simulation(
            tick_interval=tick_interval,
            activity_multiplier=activity_multiplier,
            specific_devices=specific_devices
        )

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
