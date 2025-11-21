# Battery Logger Scripts

This directory contains Python scripts for managing and simulating battery log data in the database.

## Prerequisites

Make sure you have the required Python packages installed:

```bash
pip install python-dotenv supabase
```

You also need to set up your environment variables in a `.env` file in the api directory:

```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Scripts Overview

### 📊 `create_mock_data.py`

Generates historical mock battery log entries for a single device with realistic patterns.

**Usage:**

```bash
# Generate 90 days of mock data
python scripts/create_mock_data.py

# Clear existing data and generate 30 days
python scripts/create_mock_data.py --clear --days 30

# Generate for a specific device
python scripts/create_mock_data.py --device-id pico-002 --days 60

# Custom batch size
python scripts/create_mock_data.py --batch-size 50 --days 180
```

**Options:**

- `-h, --help` - Show help message
- `--clear` - Clear all existing data before inserting new data
- `--days N` - Number of days to generate data for (default: 90)
- `--device-id ID` - Device identifier for logs (default: pico-001)
- `--batch-size N` - Number of entries to insert per batch (default: 100)

**Features:**

- Realistic collection patterns (more activity on weekdays)
- Variable amounts per collection
- Random timing throughout operational hours
- Batch insertion for performance

---

### 🏢 `simulate_multiple_devices.py`

Generates historical mock data for multiple Raspberry Pi Picos and Raspberry Pis simultaneously.

**Usage:**

```bash
# Generate data for all devices
python scripts/simulate_multiple_devices.py

# List all available devices
python scripts/simulate_multiple_devices.py --list

# Clear and generate 30 days for all devices
python scripts/simulate_multiple_devices.py --clear --days 30

# Only generate data for Pico devices
python scripts/simulate_multiple_devices.py --picos-only --days 60

# Only generate data for Raspberry Pi devices
python scripts/simulate_multiple_devices.py --pis-only

# Generate for specific devices
python scripts/simulate_multiple_devices.py --devices pico-001,pi-zero-001 --clear
```

**Options:**

- `-h, --help` - Show help message
- `--list` - List all available devices and exit
- `--clear` - Clear all existing data before inserting
- `--days N` - Number of days to generate data for (default: 90)
- `--batch-size N` - Number of entries to insert per batch (default: 100)
- `--picos-only` - Generate data only for Pico devices
- `--pis-only` - Generate data only for Raspberry Pi devices
- `--devices ID1,ID2,...` - Generate data only for specific device IDs

**Available Devices:**

**Raspberry Pi Picos:**

- `pico-001` - Building A - Floor 1
- `pico-002` - Building A - Floor 2
- `pico-003` - Building B - Floor 1
- `pico-004` - Building B - Floor 2
- `pico-005` - Building C - Main Entrance

**Raspberry Pis:**

- `pi-zero-001` - Storage Room A
- `pi-zero-002` - Storage Room B
- `pi-4-001` - Main Office
- `pi-4-002` - Workshop

**Features:**

- Multiple device simulation
- Different patterns for Picos vs Pis
- Location-based configuration
- Occasional "off days"
- Per-device statistics after completion

---

### ⚡ `live_simulate.py`

Continuously simulates battery log entries being added in real-time. Perfect for testing dashboards and real-time features.

**Usage:**

```bash
# Run with default settings (5 second ticks)
python scripts/live_simulate.py

# List all available devices
python scripts/live_simulate.py --list

# Fast simulation (1 second ticks)
python scripts/live_simulate.py --tick 1

# High activity (2x more entries)
python scripts/live_simulate.py --activity 2.0

# Slow simulation with reduced activity
python scripts/live_simulate.py --tick 10 --activity 0.5

# Simulate specific devices only
python scripts/live_simulate.py --devices pico-001,pi-4-001

# Fast testing setup
python scripts/live_simulate.py --tick 2 --activity 3.0
```

**Options:**

- `-h, --help` - Show help message
- `--list` - List all available devices and exit
- `--tick N` - Seconds between each simulation tick (default: 5)
- `--activity N` - Activity multiplier (0.1-5.0) (default: 1.0)
- `--devices ID1,ID2,...` - Simulate only specific device IDs

**Activity Rates:**
Each device has a base activity rate (probability of generating an entry per tick):

- High traffic locations: 70-90%
- Medium traffic: 50-70%
- Low traffic: 30-50%

The `--activity` multiplier scales these rates up or down.

**Features:**

- Continuous real-time simulation
- Configurable tick intervals
- Activity multiplier for faster/slower data generation
- Device-specific activity rates
- Real-time console output
- Statistics summary on exit (Ctrl+C)

**Tips:**

- Use lower tick intervals (1-2 sec) for faster testing
- Use higher activity multipliers (2-3x) to generate more data quickly
- Use specific devices to focus on particular locations
- Press Ctrl+C to stop and see statistics

---

### 🗑️ `clear_database.py`

Safely clears battery log data from the database with various filtering options.

**Usage:**

```bash
# View database statistics without clearing
python scripts/clear_database.py --stats

# Clear all data (with confirmation)
python scripts/clear_database.py --all

# Clear all data without confirmation prompt
python scripts/clear_database.py --all --force

# Clear specific devices
python scripts/clear_database.py --devices pico-001,pico-002

# Clear by date range
python scripts/clear_database.py --start 2025-01-01 --end 2025-01-31

# Clear everything from a date onwards
python scripts/clear_database.py --start 2025-11-01

# Quick device clear without confirmation
python scripts/clear_database.py --devices pi-zero-001 --force
```

**Options:**

- `-h, --help` - Show help message
- `--stats` - Show database statistics and exit (no clearing)
- `--all` - Clear all data from the database
- `--devices ID1,ID2,...` - Clear data only for specific device IDs
- `--start DATE` - Clear data from this date onwards (YYYY-MM-DD)
- `--end DATE` - Clear data up to this date (YYYY-MM-DD)
- `--force` - Skip confirmation prompt

**Features:**

- View database statistics without modifying data
- Clear all or selective data
- Filter by device IDs
- Filter by date range
- Safety confirmation prompts (unless `--force` is used)
- Before/after statistics
- Shows exactly how many entries were deleted

**Safety:**

- By default, all operations require confirmation
- Use `--force` to skip confirmation (use with caution!)
- Always check `--stats` before clearing to verify what will be deleted

---

## Common Workflows

### Initial Setup - Generate Historical Data

```bash
# Generate 90 days of data for all devices
python scripts/simulate_multiple_devices.py --clear --days 90
```

### Testing Real-Time Features

```bash
# Start live simulation in one terminal
python scripts/live_simulate.py --tick 2 --activity 2.0

# Your dashboard/app will now receive real-time data
```

### Cleaning Up Test Data

```bash
# Check what's in the database
python scripts/clear_database.py --stats

# Clear everything
python scripts/clear_database.py --all

# Or clear specific test devices
python scripts/clear_database.py --devices pico-001,pico-002 --force
```

### Generating Specific Test Scenarios

```bash
# Simulate high-traffic location data
python scripts/live_simulate.py --devices pico-005 --tick 1 --activity 3.0

# Simulate low-traffic locations over 30 days
python scripts/simulate_multiple_devices.py --devices pi-zero-001,pi-zero-002 --days 30
```

### Mixed Historical and Live Data

```bash
# Step 1: Generate 60 days of historical data
python scripts/simulate_multiple_devices.py --clear --days 60

# Step 2: Add live simulation on top
python scripts/live_simulate.py --tick 3 --activity 1.5
```

---

## Troubleshooting

### Import Errors

If you see `ImportError: No module named 'dotenv'` or similar:

```bash
pip install python-dotenv supabase
```

### Environment Variable Errors

If you see `Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY`:

1. Create a `.env` file in the `api` directory
2. Add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

### Database Connection Issues

- Verify your Supabase URL and key are correct
- Check that the `battery_logs` table exists in your database
- Ensure your service role key has the necessary permissions

### No Data Being Generated

For `live_simulate.py`:

- Try increasing the `--activity` multiplier
- Reduce the `--tick` interval
- Check the console output for error messages

---

## Script Dependencies

All scripts require:

- Python 3.7+
- `python-dotenv` package
- `supabase` Python client
- Valid `.env` file with Supabase credentials

## Database Schema

These scripts expect a `battery_logs` table with the following structure:

```sql
CREATE TABLE battery_logs (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL,
  amount INTEGER NOT NULL,
  device_id TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## License

Part of the ASEP Battery Counter project.
