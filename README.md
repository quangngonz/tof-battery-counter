# Battery Counter

A Raspberry Pi Pico W-based battery collection counter with IR sensor detection and cloud sync capabilities. This project tracks battery recycling by counting items as they pass through an IR sensor, syncing the data to a cloud API, and displaying statistics.

## Project Structure

```
battery-counter/
├── pico-battery-counter/    # MicroPython code for Raspberry Pi Pico W
│   ├── main.py              # Main program loop
│   ├── config.py            # Configuration (WiFi, API endpoints, pins)
│   ├── sensor.py            # IR sensor handler
│   ├── sync.py              # WiFi and API sync functions
│   └── tft.py               # TFT display driver wrapper
└── api/                     # Node.js Express API
    ├── index.js             # API server with Supabase integration
    └── package.json         # Node dependencies
```

## Features

- **IR Sensor Detection**: Detects batteries passing through with debouncing
- **Local Caching**: Stores counts locally when offline
- **Cloud Sync**: Automatically syncs data to a remote API
- **Statistics**: Tracks total batteries and calculates environmental impact (soil/water saved)
- **TFT Display**: Shows real-time count on connected display
- **Offline Support**: Queues records when WiFi is unavailable

## Hardware Requirements

- Raspberry Pi Pico W
- IR sensor (e.g., IR obstacle avoidance sensor)
- TFT display (optional, e.g., ILI9341)
- LED indicator (connected to GPIO 2)

## Setup

### 1. Pico W Setup

1. Install MicroPython on your Raspberry Pi Pico W
2. Edit `pico-battery-counter/config.py`:
   ```python
   SSID = "your_wifi_ssid"
   PASS = "your_wifi_password"
   API_LOG = "https://your-api.vercel.app/api/log"
   API_STATS = "https://your-api.vercel.app/api/stats"
   IR_PIN = 15  # GPIO pin for IR sensor
   ```
3. Upload all files in `pico-battery-counter/` to your Pico W
4. Connect the IR sensor to the configured GPIO pin
5. (Optional) Initialize TFT display in `main.py`

### 2. API Setup

1. Create a Supabase project and database

2. Run the SQL schema from `schema.sql` in your Supabase SQL Editor to create the `battery_logs` table

3. Install dependencies:

   ```bash
   cd api
   npm install
   ```

4. Create `.env` file:

   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

5. Run the server:

   ```bash
   npm start
   ```

6. Deploy to Vercel or your preferred platform

## API Endpoints

### POST `/log`

Log a battery count event

```json
{
  "timestamp": 1234567890,
  "amount": 1
}
```

### GET `/stats`

Get statistics

```json
{
  "total": 150,
  "soil": 3.0,
  "water": 22.5
}
```

## Environmental Impact Calculation

- **Soil saved**: 0.02 kg per battery
- **Water saved**: 0.15 L per battery

## How It Works

1. IR sensor detects battery passing through
2. Count is stored locally in `cache.json`
3. Pico W connects to WiFi and syncs cached data to API
4. API stores data in Supabase database
5. Statistics are fetched and displayed on TFT screen
6. LED blinks to indicate activity

## License

ISC

## Author

Quang Ngo
