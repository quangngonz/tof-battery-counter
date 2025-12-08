import os
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
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

# Hanoi timezone
HANOI_TZ = ZoneInfo("Asia/Ho_Chi_Minh")  # GMT+7


def generate_school_day_timestamps(date, num_entries):
    """
    Generate realistic timestamps for battery collections during a school day.

    School schedule:
    - 7:10-7:15: Kids arrive
    - 7:30: School starts
    - 9:30-10:30: Break (peak collection time)
    - 11:30-1:30: Lunch (peak collection time)
    - 2:30-2:50: Afternoon tea
    - 4:30: School ends
    - 6:30: No one at school

    Args:
        date: datetime object for the target date
        num_entries: Number of entries to generate

    Returns:
        List of datetime objects in Hanoi timezone
    """
    timestamps = []

    # Define time windows with their weights (probability of battery collection)
    time_windows = [
        # (start_hour, start_min, end_hour, end_min, weight)
        (7, 10, 7, 25, 15),      # Arrival time - moderate
        (7, 25, 9, 30, 10),      # Morning classes - low
        (9, 30, 10, 30, 30),     # Break - HIGH
        (10, 30, 11, 30, 8),     # Late morning - low
        (11, 30, 13, 30, 35),    # Lunch - HIGHEST
        (13, 30, 14, 30, 12),    # Early afternoon - moderate
        (14, 30, 14, 50, 20),    # Afternoon tea - high
        (14, 50, 16, 30, 10),    # Late afternoon - low
        (16, 30, 17, 30, 5),     # After school - very low
    ]

    # Calculate total weight
    total_weight = sum(w[4] for w in time_windows)

    # Distribute entries across time windows based on weights
    for _ in range(num_entries):
        # Select a time window based on weights
        rand_val = random.random() * total_weight
        cumulative = 0
        selected_window = None

        for window in time_windows:
            cumulative += window[4]
            if rand_val <= cumulative:
                selected_window = window
                break

        if selected_window is None:
            selected_window = time_windows[-1]

        start_h, start_m, end_h, end_m, _ = selected_window

        # Convert to minutes from midnight
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m

        # Random time within the window
        random_minutes = random.randint(start_minutes, end_minutes)
        hour = random_minutes // 60
        minute = random_minutes % 60
        second = random.randint(0, 59)

        # Create timestamp in Hanoi timezone
        timestamp = datetime(
            date.year, date.month, date.day,
            hour, minute, second,
            tzinfo=HANOI_TZ
        )

        timestamps.append(timestamp)

    # Sort timestamps chronologically
    timestamps.sort()

    return timestamps


def add_manual_batteries(num_batteries=120, device_id="pico-001", batch_size=50):
    """
    Manually add battery entries for today with realistic school schedule timestamps.

    Args:
        num_batteries: Number of battery entries to add (default 120)
        device_id: Device identifier for the logs
        batch_size: Number of entries to insert per batch
    """
    print(f"🔋 Adding {num_batteries} battery entries for today...")

    # Get today's date in Hanoi timezone
    today = datetime.now(HANOI_TZ).replace(
        hour=0, minute=0, second=0, microsecond=0)

    print(f"📅 Date: {today.strftime('%Y-%m-%d')} (Hanoi GMT+7)")
    print(f"🏫 Simulating school day battery collections...")

    # Generate timestamps
    timestamps = generate_school_day_timestamps(today, num_batteries)

    # Create entries
    entries = []
    for timestamp in timestamps:
        entry = {
            'device_id': device_id,
            'amount': 1,  # Individual entries of 1 battery at a time
            'timestamp': timestamp.isoformat()
        }
        entries.append(entry)

    # Insert in batches
    total_inserted = 0
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        try:
            result = supabase.table('battery_logs').insert(batch).execute()
            total_inserted += len(batch)
            print(
                f"✅ Inserted batch {i // batch_size + 1}: {len(batch)} entries ({total_inserted}/{num_batteries})")
        except Exception as e:
            print(f"❌ Error inserting batch {i // batch_size + 1}: {str(e)}")
            continue

    print(f"\n🎉 Successfully added {total_inserted} battery entries!")

    # Show time distribution
    print("\n📊 Time distribution:")
    morning = sum(1 for t in timestamps if 7 <= t.hour < 10)
    break_time = sum(1 for t in timestamps if 9 <= t.hour < 11)
    lunch = sum(1 for t in timestamps if 11 <= t.hour < 14)
    afternoon = sum(1 for t in timestamps if 14 <= t.hour < 17)

    print(f"   7:00-10:00 (Morning/Arrival): {morning} entries")
    print(f"   9:30-11:00 (Break): {break_time} entries")
    print(f"   11:30-14:00 (Lunch): {lunch} entries")
    print(f"   14:00-17:30 (Afternoon/Tea): {afternoon} entries")

    # Show first and last timestamps
    if timestamps:
        print(f"\n⏰ First entry: {timestamps[0].strftime('%H:%M:%S')}")
        print(f"⏰ Last entry: {timestamps[-1].strftime('%H:%M:%S')}")


if __name__ == "__main__":
    # Add 120 batteries with realistic school day pattern
    add_manual_batteries(num_batteries=120, device_id="pico-001")
