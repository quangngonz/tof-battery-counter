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


def create_mock_data(num_days=90, device_id="pico-001"):
    """
    Create mock battery log entries with realistic patterns over multiple months

    Args:
        num_days: Number of days to generate data for (default 90 = ~3 months)
        device_id: Device identifier for the logs
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
            1, 3) if is_weekend else random.randint(2, 4)

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

    # Insert in batches to avoid request size limits
    batch_size = 100
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


def main():
    """Main execution function"""
    try:
        # Clear existing data
        clear_all_data()

        # Create mock data for the last 90 days (~3 months)
        create_mock_data(num_days=90, device_id="pico-001")

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
