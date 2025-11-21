import os
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


def get_database_stats():
    """Get current database statistics"""
    try:
        result = supabase.table('battery_logs').select(
            'count', count='exact').execute()
        total_count = result.count

        # Get device breakdown
        all_data = supabase.table('battery_logs').select('device_id').execute()
        device_counts = {}
        for row in all_data.data:
            device_id = row['device_id']
            device_counts[device_id] = device_counts.get(device_id, 0) + 1

        return total_count, device_counts
    except Exception as e:
        print(f"❌ Error getting database stats: {str(e)}")
        return None, None


def clear_all_data():
    """Clear all data from battery_logs table"""
    try:
        supabase.table('battery_logs').delete().neq('id', 0).execute()
        return True
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
        return False


def clear_by_device(device_ids):
    """Clear data for specific devices"""
    try:
        for device_id in device_ids:
            supabase.table('battery_logs').delete().eq(
                'device_id', device_id).execute()
            print(f"✅ Cleared data for device: {device_id}")
        return True
    except Exception as e:
        print(f"❌ Error clearing device data: {str(e)}")
        return False


def clear_by_date_range(start_date=None, end_date=None):
    """Clear data within a date range"""
    try:
        query = supabase.table('battery_logs').delete()

        if start_date:
            query = query.gte('timestamp', start_date)
        if end_date:
            query = query.lte('timestamp', end_date)

        query.neq('id', 0).execute()
        return True
    except Exception as e:
        print(f"❌ Error clearing date range: {str(e)}")
        return False


def confirm_action(prompt):
    """Ask user for confirmation"""
    response = input(f"{prompt} (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def print_help():
    """Print help message"""
    help_text = """
Battery Logger Database Cleaner

Clears battery log data from the database with various options.

Usage:
    python clear_database.py [OPTIONS]

Options:
    -h, --help              Show this help message
    --all                   Clear all data from the database
    --devices ID1,ID2,...   Clear data only for specific device IDs (comma-separated)
    --start DATE           Clear data from this date onwards (YYYY-MM-DD)
    --end DATE             Clear data up to this date (YYYY-MM-DD)
    --force                Skip confirmation prompt
    --stats                Show database statistics and exit

Examples:
    python clear_database.py --stats
        Show current database statistics without clearing

    python clear_database.py --all
        Clear all data (will ask for confirmation)

    python clear_database.py --all --force
        Clear all data without confirmation

    python clear_database.py --devices pico-001,pico-002
        Clear data only for pico-001 and pico-002

    python clear_database.py --start 2025-01-01
        Clear all data from January 1, 2025 onwards

    python clear_database.py --start 2025-01-01 --end 2025-01-31
        Clear data only from January 2025

    python clear_database.py --devices pi-zero-001 --force
        Clear pi-zero-001 data without confirmation

Safety:
    - By default, all operations require confirmation
    - Use --force to skip confirmation (use with caution!)
    - Always check --stats before clearing to verify what will be deleted
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

        # Get current database stats
        total_count, device_counts = get_database_stats()

        if total_count is None:
            print("❌ Failed to retrieve database statistics")
            return 1

        # Check for stats flag
        if '--stats' in sys.argv:
            print("\n📊 Database Statistics")
            print("=" * 60)
            print(f"Total entries: {total_count}")
            if device_counts:
                print("\nEntries per device:")
                for device_id, count in sorted(device_counts.items()):
                    print(f"  • {device_id:<15} : {count:>6} entries")
            print("=" * 60)
            return 0

        # Check if database is already empty
        if total_count == 0:
            print("ℹ️  Database is already empty (0 entries)")
            return 0

        # Parse flags
        force = '--force' in sys.argv
        clear_all = '--all' in sys.argv

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

        # Parse --start and --end arguments
        start_date = None
        end_date = None
        if '--start' in sys.argv:
            try:
                start_index = sys.argv.index('--start')
                start_date = sys.argv[start_index + 1]
            except IndexError:
                print("❌ Error: --start requires a date (YYYY-MM-DD)")
                return 1

        if '--end' in sys.argv:
            try:
                end_index = sys.argv.index('--end')
                end_date = sys.argv[end_index + 1]
            except IndexError:
                print("❌ Error: --end requires a date (YYYY-MM-DD)")
                return 1

        # Validate that at least one clear option is specified
        if not (clear_all or specific_devices or start_date or end_date):
            print(
                "❌ Error: Please specify what to clear (--all, --devices, --start, --end)")
            print("   Use --help for usage information")
            return 1

        # Show current state
        print("\n🗄️  Current Database State")
        print("=" * 60)
        print(f"Total entries: {total_count}")
        if device_counts:
            print("\nEntries per device:")
            for device_id, count in sorted(device_counts.items()):
                print(f"  • {device_id:<15} : {count:>6} entries")
        print("=" * 60)

        # Determine what will be cleared
        print("\n⚠️  Clear Operation")
        print("=" * 60)

        if clear_all:
            print("Operation: Clear ALL data")
            print(f"This will delete all {total_count} entries")
        elif specific_devices:
            print(f"Operation: Clear data for specific devices")
            print(f"Devices: {', '.join(specific_devices)}")
            device_total = sum(device_counts.get(
                d, 0) for d in specific_devices)
            print(f"This will delete approximately {device_total} entries")
        elif start_date or end_date:
            print("Operation: Clear data by date range")
            if start_date and end_date:
                print(f"Date range: {start_date} to {end_date}")
            elif start_date:
                print(f"From: {start_date} onwards")
            elif end_date:
                print(f"Up to: {end_date}")

        print("=" * 60)

        # Confirm action
        if not force:
            if not confirm_action("\n⚠️  Are you sure you want to proceed?"):
                print("\n❌ Operation cancelled by user")
                return 0

        # Perform the clear operation
        print("\n🗑️  Clearing data...")

        success = False
        if clear_all:
            success = clear_all_data()
            if success:
                print("✅ All data cleared successfully!")
        elif specific_devices:
            success = clear_by_device(specific_devices)
            if success:
                print(
                    f"✅ Data cleared for {len(specific_devices)} device(s)")
        elif start_date or end_date:
            success = clear_by_date_range(start_date, end_date)
            if success:
                print("✅ Data cleared for specified date range")

        if not success:
            print("❌ Failed to clear data")
            return 1

        # Show new state
        new_total_count, new_device_counts = get_database_stats()
        if new_total_count is not None:
            print("\n📊 Updated Database State")
            print("=" * 60)
            print(f"Total entries: {new_total_count}")
            if new_device_counts:
                print("\nRemaining entries per device:")
                for device_id, count in sorted(new_device_counts.items()):
                    print(f"  • {device_id:<15} : {count:>6} entries")
            print("=" * 60)
            print(
                f"\n✅ Successfully deleted {total_count - new_total_count} entries")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
