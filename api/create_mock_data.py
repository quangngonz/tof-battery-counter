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


def clear_all_data():
    """Clear all existing data from battery_logs table"""
    print("Clearing existing data...")
    try:
        # Delete all records
        supabase.table('battery_logs').delete().neq('id', 0).execute()
        print("✅ All existing data cleared!")
    except Exception as e:
        print(f"Error clearing data: {str(e)}")


def create_mock_data(num_days=90, device_id="pico-001", batch_size=100, clear_existing=True):
    """
    Create mock battery log entries with realistic patterns over multiple months

    Args:
        num_days: Number of days to generate data for (default 90 = ~3 months)
        device_id: Device identifier for the logs
        batch_size: Number of entries to insert per batch
    """
    print(f"Creating mock battery log entries for the last {num_days} days...")

    end_time = datetime.now()
    start_time = end_time - timedelta(days=num_days)

    entries = []
    current_date = start_time

    # Generate data for each day
    while current_date <= end_time:
        # Simulate realistic collection patterns
        # Weekdays: 2-4 entries per day
        # Weekends: 1-3 entries per day
        is_weekend = current_date.weekday() in [5, 6]
        num_entries_today = random.randint(
            1, 3) if is_weekend else random.randint(2, 10)

        for _ in range(num_entries_today):
            # Random time during the day (8 AM to 8 PM)
            hour = random.randint(8, 20)
            minute = random.randint(0, 59)
            timestamp = current_date.replace(
                hour=hour, minute=minute, second=0)

            # Varying amounts: mostly 1-3, occasionally more
            if random.random() < 0.8:
                amount = random.randint(1, 3)
            else:
                amount = random.randint(4, 8)

            entries.append({
                'timestamp': timestamp.isoformat(),
                'amount': amount,
                'device_id': device_id
            })

        current_date += timedelta(days=1)

    # Sort by timestamp for better data organization
    entries.sort(key=lambda x: x['timestamp'])

    print(f"Generated {len(entries)} entries total")

    if clear_existing:
        clear_all_data()

    # Insert in batches to avoid request size limits
    total_inserted = 0

    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        try:
            response = supabase.table('battery_logs').insert(batch).execute()
            total_inserted += len(batch)
            print(
                f"Inserted batch {i//batch_size + 1}: {len(batch)} entries (Total: {total_inserted}/{len(entries)})")
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1}: {str(e)}")
            continue

    print(f"\n✅ Successfully inserted {total_inserted} mock entries!")
    return total_inserted


def print_help():
    """Print help message"""
    help_text = """
Battery Logger Mock Data Generator

Usage:
    python create_mock_data.py [OPTIONS]

Options:
    -h, --help              Show this help message and exit
    --clear                 Clear all existing data before inserting new data
    --days N               Number of days to generate data for (default: 90)
    --device-id ID         Device identifier for logs (default: pico-001)
    --batch-size N         Number of entries to insert per batch (default: 100)

Examples:
    python create_mock_data.py
        Generate 90 days of mock data without clearing existing data

    python create_mock_data.py --clear
        Clear existing data and generate 90 days of mock data

    python create_mock_data.py --days 30 --device-id pico-002
        Generate 30 days of mock data for device pico-002

    python create_mock_data.py --clear --days 180 --batch-size 50
        Clear data and generate 180 days with batch size of 50
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

        # Parse command line arguments
        clear_existing = '--clear' in sys.argv

        # Parse --days argument
        num_days = 90
        if '--days' in sys.argv:
            try:
                days_index = sys.argv.index('--days')
                num_days = int(sys.argv[days_index + 1])
            except (IndexError, ValueError):
                print("❌ Error: --days requires a valid integer argument")
                return 1

        # Parse --device-id argument
        device_id = "pico-001"
        if '--device-id' in sys.argv:
            try:
                device_index = sys.argv.index('--device-id')
                device_id = sys.argv[device_index + 1]
            except IndexError:
                print("❌ Error: --device-id requires a value")
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

        # Create mock data
        create_mock_data(
            num_days=num_days,
            device_id=device_id,
            batch_size=batch_size,
            clear_existing=clear_existing
        )

        # Verify the data
        print("\nVerifying data...")
        result = supabase.table('battery_logs').select(
            'count', count='exact').execute()
        print(f"Total entries in database: {result.count}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
