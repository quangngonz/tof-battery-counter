import os
import sys
import random
import argparse
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


def get_current_school_period(current_time):
    """
    Determine the current school period based on time.

    Returns:
        tuple: (period_name, start_time, end_time) or None if outside school hours
    """
    hour = current_time.hour
    minute = current_time.minute
    current_minutes = hour * 60 + minute

    periods = [
        ("Arrival", (7, 10), (7, 25)),
        ("Morning Classes", (7, 25), (9, 30)),
        ("Break", (9, 30), (10, 30)),
        ("Late Morning", (10, 30), (11, 30)),
        ("Lunch", (11, 30), (13, 30)),
        ("Early Afternoon", (13, 30), (14, 30)),
        ("Afternoon Tea", (14, 30), (14, 50)),
        ("Late Afternoon", (14, 50), (16, 30)),
        ("After School", (16, 30), (17, 30)),
    ]

    for period_name, (start_h, start_m), (end_h, end_m) in periods:
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m

        if start_minutes <= current_minutes <= end_minutes:
            return period_name, (start_h, start_m), (end_h, end_m)

    # Before school or after school hours
    if current_minutes < 7 * 60 + 10:
        return None, None, None
    elif current_minutes > 17 * 60 + 30:
        return "After Hours", (16, 30), (17, 30)

    return None, None, None


def generate_school_day_timestamps(date, num_entries, end_time=None):
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
        end_time: Optional datetime to limit entries up to this time (for live mode)

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

    # Filter time windows if end_time is specified
    if end_time:
        end_minutes = end_time.hour * 60 + end_time.minute
        filtered_windows = []

        for start_h, start_m, end_h, end_m, weight in time_windows:
            window_start = start_h * 60 + start_m
            window_end = end_h * 60 + end_m

            # Skip windows that start after end_time
            if window_start >= end_minutes:
                continue

            # Adjust window end if it goes past end_time
            if window_end > end_minutes:
                end_h = end_minutes // 60
                end_m = end_minutes % 60

            filtered_windows.append((start_h, start_m, end_h, end_m, weight))

        time_windows = filtered_windows

    # Calculate total weight
    total_weight = sum(w[4] for w in time_windows)

    if total_weight == 0:
        print("⚠️  No valid time windows found")
        return []

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


def add_manual_batteries(num_batteries=120, target_count=None, device_id="pico-001", batch_size=50, live_mode=False):
    """
    Manually add battery entries for today with realistic school schedule timestamps.

    Args:
        num_batteries: Number of battery entries to add (default 120)
        target_count: Target total count to reach (mutually exclusive with num_batteries)
        device_id: Device identifier for the logs
        batch_size: Number of entries to insert per batch
        live_mode: If True, only add entries up to current time
    """
    # Get current time in Hanoi timezone
    now = datetime.now(HANOI_TZ)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # If target_count is specified, calculate how many to add
    if target_count is not None:
        # Get current count for today
        today_start = today.isoformat()
        today_end = (today + timedelta(days=1)).isoformat()

        try:
            result = supabase.table('battery_logs')\
                .select('amount', count='exact')\
                .eq('device_id', device_id)\
                .gte('timestamp', today_start)\
                .lt('timestamp', today_end)\
                .execute()

            current_count = sum(row['amount']
                                for row in result.data) if result.data else 0
            print(f"📊 Current count for today: {current_count}")

            if current_count >= target_count:
                print(
                    f"✅ Already at or above target ({target_count}). No entries needed.")
                return

            num_batteries = target_count - current_count
            print(f"🎯 Target: {target_count} | Need to add: {num_batteries}")
        except Exception as e:
            print(f"❌ Error fetching current count: {str(e)}")
            return

    if live_mode:
        period_name, start_time, end_time = get_current_school_period(now)

        if period_name is None:
            print(f"⚠️  Current time: {now.strftime('%H:%M:%S')}")
            print(f"❌ Outside school hours (7:10 AM - 5:30 PM)")
            return

        print(f"⏰ Current time: {now.strftime('%H:%M:%S')} (Hanoi GMT+7)")
        print(f"📚 Current period: {period_name}")

        # Ask user for number of batteries
        try:
            user_input = input(
                f"\n🔋 How many batteries to add? (default: {num_batteries}): ").strip()
            if user_input:
                num_batteries = int(user_input)
        except ValueError:
            print(f"Invalid input. Using default: {num_batteries}")
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user")
            return

        print(
            f"\n🔋 Adding {num_batteries} battery entries from 7:10 AM to now ({now.strftime('%H:%M:%S')})...")
        print(f"📅 Date: {today.strftime('%Y-%m-%d')} (Hanoi GMT+7)")

        # Generate timestamps up to current time
        timestamps = generate_school_day_timestamps(
            today, num_batteries, end_time=now)
    else:
        print(
            f"🔋 Adding {num_batteries} battery entries for full school day...")
        print(f"📅 Date: {today.strftime('%Y-%m-%d')} (Hanoi GMT+7)")
        print(f"🏫 Simulating school day battery collections...")

        # Generate timestamps for full day
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
    parser = argparse.ArgumentParser(
        description='Add battery entries to the database with realistic school day timestamps'
    )
    parser.add_argument(
        '--live-time',
        action='store_true',
        help='Live mode: Ask for battery count and add entries up to current time only'
    )

    # Create mutually exclusive group for -n and --target
    count_group = parser.add_mutually_exclusive_group()
    count_group.add_argument(
        '-n', '--num-batteries',
        type=int,
        default=120,
        help='Number of battery entries to add (default: 120, ignored in live mode unless specified)'
    )
    count_group.add_argument(
        '--target',
        type=int,
        help='Target total count to reach for today (will calculate and add the difference)'
    )

    parser.add_argument(
        '-d', '--device-id',
        type=str,
        default='pico-001',
        help='Device ID for the entries (default: pico-001)'
    )

    args = parser.parse_args()

    # Add batteries with specified parameters
    add_manual_batteries(
        num_batteries=args.num_batteries if args.target is None else None,
        target_count=args.target,
        device_id=args.device_id,
        live_mode=args.live_time
    )
