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


def remove_batteries_to_target(target_count, device_id=None, dry_run=False):
    """
    Randomly remove battery entries from today until the total overall count reaches the target.

    Args:
        target_count: Target total count to reach (all-time)
        device_id: Device identifier for the logs (None = all devices)
        dry_run: If True, only show what would be removed without actually removing
    """
    try:
        # Get current total count (all-time) - same logic as API
        query = supabase.table('battery_logs').select('amount')
        if device_id:
            query = query.eq('device_id', device_id)
        result = query.execute()

        current_total = sum(record.get('amount', 0)
                            for record in result.data) if result.data else 0
        print(f"📊 Current total count (all-time): {current_total}")
        print(f"🎯 Target count: {target_count}")

        if current_total <= target_count:
            print(f"✅ Already at or below target. No entries need to be removed.")
            return

        num_to_remove = current_total - target_count
        print(f"🗑️  Need to remove: {num_to_remove} batteries")

        # Get today's date range
        now = datetime.now(HANOI_TZ)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_start = today.isoformat()
        today_end = (today + timedelta(days=1)).isoformat()

        # Get all entries from today
        query = supabase.table('battery_logs')\
            .select('id', 'amount', 'timestamp')\
            .gte('timestamp', today_start)\
            .lt('timestamp', today_end)\
            .order('timestamp')
        if device_id:
            query = query.eq('device_id', device_id)
        result = query.execute()

        today_entries = result.data if result.data else []
        today_total = sum(entry['amount'] for entry in today_entries)

        print(
            f"📅 Today's entries: {len(today_entries)} records ({today_total} batteries)")

        if not today_entries:
            print("❌ No entries found for today to remove.")
            return

        if today_total < num_to_remove:
            print(
                f"⚠️  Warning: Today only has {today_total} batteries, but need to remove {num_to_remove}.")
            print(f"           Will remove all {today_total} from today.")
            num_to_remove = today_total

        # Randomly select entries to remove
        # Create a list where each entry appears 'amount' times (to respect individual batteries)
        battery_pool = []
        for entry in today_entries:
            for _ in range(entry['amount']):
                battery_pool.append(entry['id'])

        # Randomly select IDs to remove
        random.shuffle(battery_pool)
        ids_to_remove = battery_pool[:num_to_remove]

        # Count how many of each ID
        id_counts = {}
        for id_val in ids_to_remove:
            id_counts[id_val] = id_counts.get(id_val, 0) + 1

        print(f"\n{'🔍' if dry_run else '🗑️ '} {'Would remove' if dry_run else 'Removing'} {len(id_counts)} entries:")

        removed_count = 0
        for entry_id, count in id_counts.items():
            entry = next(e for e in today_entries if e['id'] == entry_id)
            original_amount = entry['amount']
            new_amount = original_amount - count

            timestamp_str = datetime.fromisoformat(entry['timestamp'].replace(
                'Z', '+00:00')).astimezone(HANOI_TZ).strftime('%H:%M:%S')

            if dry_run:
                if new_amount == 0:
                    print(
                        f"   - ID {entry_id}: Remove entire entry ({original_amount} batteries) at {timestamp_str}")
                else:
                    print(
                        f"   - ID {entry_id}: {original_amount} → {new_amount} batteries at {timestamp_str}")
            else:
                try:
                    if new_amount == 0:
                        # Delete entire entry
                        supabase.table('battery_logs').delete().eq(
                            'id', entry_id).execute()
                        print(
                            f"   ✅ Deleted entry {entry_id} ({original_amount} batteries) at {timestamp_str}")
                    else:
                        # Update with reduced amount
                        supabase.table('battery_logs').update(
                            {'amount': new_amount}).eq('id', entry_id).execute()
                        print(
                            f"   ✅ Updated entry {entry_id}: {original_amount} → {new_amount} batteries at {timestamp_str}")

                    removed_count += count
                except Exception as e:
                    print(f"   ❌ Error processing entry {entry_id}: {str(e)}")

        if dry_run:
            print(
                f"\n🔍 Dry run complete. Would have removed {num_to_remove} batteries.")
            print(f"💡 Run without --dry-run to actually remove entries.")
        else:
            print(f"\n🎉 Successfully removed {removed_count} batteries!")

            # Verify new total
            query = supabase.table('battery_logs').select('amount')
            if device_id:
                query = query.eq('device_id', device_id)
            result = query.execute()

            new_total = sum(record.get('amount', 0)
                            for record in result.data) if result.data else 0
            print(f"📊 New total count: {new_total}")

            if new_total == target_count:
                print(f"✅ Target reached exactly!")
            elif new_total < target_count:
                print(f"⚠️  Below target by {target_count - new_total}")
            else:
                print(f"⚠️  Above target by {new_total - target_count}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Remove battery entries from today until total count reaches target'
    )
    parser.add_argument(
        'target',
        type=int,
        help='Target total count to reach (all-time)'
    )
    parser.add_argument(
        '-d', '--device-id',
        type=str,
        default=None,
        help='Device ID for the entries (default: all devices)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be removed without actually removing'
    )

    args = parser.parse_args()

    # Remove batteries to reach target
    remove_batteries_to_target(
        target_count=args.target,
        device_id=args.device_id,
        dry_run=args.dry_run
    )
