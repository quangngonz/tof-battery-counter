import os
import random
from datetime import datetime, timedelta
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

# Define different device types and their IDs
DEVICE_CONFIGS = {
    'picos': [
        {'id': 'pico-001', 'location': 'Building A - Floor 1'},
        {'id': 'pico-002', 'location': 'Building A - Floor 2'},
        {'id': 'pico-003', 'location': 'Building B - Floor 1'},
        {'id': 'pico-004', 'location': 'Building B - Floor 2'},
        {'id': 'pico-005', 'location': 'Building C - Main Entrance'},
    ],
    'pis': [
        {'id': 'pi-zero-001', 'location': 'Storage Room A'},
        {'id': 'pi-zero-002', 'location': 'Storage Room B'},
        {'id': 'pi-4-001', 'location': 'Main Office'},
        {'id': 'pi-4-002', 'location': 'Workshop'},
    ]
}


def clear_all_data():
    """Clear all existing data from battery_logs table"""
    print("Clearing existing data...")
    try:
        supabase.table('battery_logs').delete().neq('id', 0).execute()
        print("✅ All existing data cleared!")
    except Exception as e:
        print(f"Error clearing data: {str(e)}")


def generate_device_entries(device_id, device_type, num_days, start_time):
    """
    Generate entries for a specific device with realistic patterns

    Args:
        device_id: The device identifier
        device_type: 'pico' or 'pi'
        num_days: Number of days to generate data for
        start_time: Starting datetime

    Returns:
        List of entry dictionaries
    """
    entries = []
    current_date = start_time
    end_time = start_time + timedelta(days=num_days)

    # Different patterns for different device types
    if device_type == 'pico':
        # Picos might have more frequent but smaller collections
        base_entries_weekday = (3, 8)
        base_entries_weekend = (1, 4)
        amount_range_common = (1, 2)
        amount_range_rare = (3, 5)
    else:  # pi
        # Raspberry Pis might have less frequent but larger collections
        base_entries_weekday = (2, 6)
        base_entries_weekend = (1, 3)
        amount_range_common = (2, 4)
        amount_range_rare = (5, 10)

    while current_date <= end_time:
        # Determine entries based on day type
        is_weekend = current_date.weekday() in [5, 6]

        if is_weekend:
            num_entries_today = random.randint(*base_entries_weekend)
        else:
            num_entries_today = random.randint(*base_entries_weekday)

        # Occasionally have "off days" with no collections (10% chance)
        if random.random() < 0.1:
            num_entries_today = 0

        for _ in range(num_entries_today):
            # Random time during operational hours (7 AM to 9 PM)
            hour = random.randint(7, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            timestamp = current_date.replace(
                hour=hour, minute=minute, second=second)

            # Varying amounts based on probability
            if random.random() < 0.85:  # 85% of the time
                amount = random.randint(*amount_range_common)
            else:  # 15% of the time - larger collections
                amount = random.randint(*amount_range_rare)

            entries.append({
                'timestamp': timestamp.isoformat(),
                'amount': amount,
                'device_id': device_id
            })

        current_date += timedelta(days=1)

    return entries


def simulate_multiple_devices(num_days=90, batch_size=100, clear_existing=True,
                              include_picos=True, include_pis=True,
                              specific_devices=None):
    """
    Simulate battery log entries from multiple Picos and Raspberry Pis

    Args:
        num_days: Number of days to generate data for (default 90)
        batch_size: Number of entries to insert per batch
        clear_existing: Whether to clear existing data first
        include_picos: Whether to include Pico devices
        include_pis: Whether to include Pi devices
        specific_devices: List of specific device IDs to generate data for (overrides include flags)
    """
    print(
        f"🔋 Simulating battery logs from multiple devices for the last {num_days} days...")

    end_time = datetime.now()
    start_time = end_time - timedelta(days=num_days)

    all_entries = []

    # Determine which devices to generate data for
    devices_to_simulate = []

    if specific_devices:
        # Use specific devices if provided
        for device_list in [DEVICE_CONFIGS['picos'], DEVICE_CONFIGS['pis']]:
            for device in device_list:
                if device['id'] in specific_devices:
                    device_type = 'pico' if device['id'].startswith(
                        'pico') else 'pi'
                    devices_to_simulate.append((device, device_type))
    else:
        # Otherwise use flags to determine which device types to include
        if include_picos:
            devices_to_simulate.extend([(d, 'pico')
                                       for d in DEVICE_CONFIGS['picos']])
        if include_pis:
            devices_to_simulate.extend([(d, 'pi')
                                       for d in DEVICE_CONFIGS['pis']])

    # Generate entries for each device
    for device, device_type in devices_to_simulate:
        device_id = device['id']
        location = device['location']
        print(f"\n📍 Generating data for {device_id} ({location})...")

        device_entries = generate_device_entries(
            device_id=device_id,
            device_type=device_type,
            num_days=num_days,
            start_time=start_time
        )

        all_entries.extend(device_entries)
        print(f"   Generated {len(device_entries)} entries")

    # Sort all entries by timestamp
    all_entries.sort(key=lambda x: x['timestamp'])

    print(f"\n📊 Total entries generated: {len(all_entries)}")
    print(f"   From {len(devices_to_simulate)} devices")

    if clear_existing:
        clear_all_data()

    # Insert in batches
    total_inserted = 0
    total_batches = (len(all_entries) + batch_size - 1) // batch_size

    print(f"\n⏳ Inserting data in {total_batches} batches...")

    for i in range(0, len(all_entries), batch_size):
        batch = all_entries[i:i + batch_size]
        try:
            response = supabase.table('battery_logs').insert(batch).execute()
            total_inserted += len(batch)
            progress = (total_inserted / len(all_entries)) * 100
            print(f"   Batch {i//batch_size + 1}/{total_batches}: {len(batch)} entries "
                  f"({progress:.1f}% complete)")
        except Exception as e:
            print(f"   ❌ Error inserting batch {i//batch_size + 1}: {str(e)}")
            continue

    print(
        f"\n✅ Successfully inserted {total_inserted}/{len(all_entries)} entries!")
    return total_inserted


def print_device_list():
    """Print list of all available devices"""
    print("\n📱 Available Devices:\n")
    print("Raspberry Pi Picos:")
    for device in DEVICE_CONFIGS['picos']:
        print(f"  • {device['id']:<15} - {device['location']}")

    print("\nRaspberry Pis:")
    for device in DEVICE_CONFIGS['pis']:
        print(f"  • {device['id']:<15} - {device['location']}")
    print()


def print_help():
    """Print help message"""
    help_text = """
Battery Logger Multi-Device Simulator

Usage:
    python simulate_multiple_devices.py [OPTIONS]

Options:
    -h, --help              Show this help message
    --list                  List all available devices and exit
    --clear                 Clear all existing data before inserting new data
    --days N               Number of days to generate data for (default: 90)
    --batch-size N         Number of entries to insert per batch (default: 100)
    --picos-only           Generate data only for Pico devices
    --pis-only             Generate data only for Raspberry Pi devices
    --devices ID1,ID2,...  Generate data only for specific device IDs (comma-separated)

Examples:
    python simulate_multiple_devices.py
        Generate 90 days of data for all devices without clearing existing data

    python simulate_multiple_devices.py --clear --days 30
        Clear existing data and generate 30 days for all devices

    python simulate_multiple_devices.py --picos-only --days 60
        Generate 60 days of data only for Pico devices

    python simulate_multiple_devices.py --pis-only
        Generate 90 days of data only for Raspberry Pi devices

    python simulate_multiple_devices.py --devices pico-001,pi-zero-001 --clear
        Clear data and generate entries only for pico-001 and pi-zero-001

    python simulate_multiple_devices.py --list
        List all available devices
"""
    print(help_text)


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

        # Parse command line arguments
        clear_existing = '--clear' in sys.argv
        picos_only = '--picos-only' in sys.argv
        pis_only = '--pis-only' in sys.argv

        # Parse --days argument
        num_days = 90
        if '--days' in sys.argv:
            try:
                days_index = sys.argv.index('--days')
                num_days = int(sys.argv[days_index + 1])
            except (IndexError, ValueError):
                print("❌ Error: --days requires a valid integer argument")
                return 1

        # Parse --batch-size argument
        batch_size = 100
        if '--batch-size' in sys.argv:
            try:
                batch_index = sys.argv.index('--batch-size')
                batch_size = int(sys.argv[batch_index + 1])
            except (IndexError, ValueError):
                print("❌ Error: --batch-size requires a valid integer argument")
                return 1

        # Parse --devices argument
        specific_devices = None
        if '--devices' in sys.argv:
            try:
                devices_index = sys.argv.index('--devices')
                devices_str = sys.argv[devices_index + 1]
                specific_devices = [d.strip() for d in devices_str.split(',')]
                print(
                    f"🎯 Targeting specific devices: {', '.join(specific_devices)}")
            except IndexError:
                print("❌ Error: --devices requires comma-separated device IDs")
                return 1

        # Determine which device types to include
        include_picos = not pis_only
        include_pis = not picos_only

        if specific_devices:
            include_picos = True
            include_pis = True

        # Simulate multiple devices
        simulate_multiple_devices(
            num_days=num_days,
            batch_size=batch_size,
            clear_existing=clear_existing,
            include_picos=include_picos,
            include_pis=include_pis,
            specific_devices=specific_devices
        )

        # Verify the data
        print("\n🔍 Verifying data...")
        result = supabase.table('battery_logs').select(
            'count', count='exact').execute()
        print(f"   Total entries in database: {result.count}")

        # Get per-device counts
        device_counts = supabase.table('battery_logs').select(
            'device_id', count='exact').execute()

        # Group by device_id
        print("\n📈 Entries per device:")
        all_devices = [d['id']
                       for d in DEVICE_CONFIGS['picos'] + DEVICE_CONFIGS['pis']]
        for device_id in all_devices:
            device_result = supabase.table('battery_logs').select(
                'count', count='exact').eq('device_id', device_id).execute()
            if device_result.count > 0:
                print(f"   {device_id:<15} : {device_result.count:>6} entries")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
