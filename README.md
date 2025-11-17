# Battery Counter

A Raspberry Pi Pico W-based battery collection counter with IR sensor detection and cloud sync capabilities. This project tracks battery recycling by counting items as they pass through an IR sensor, syncing the data to a cloud API, and displaying statistics.

## Project Structure

```txt
battery-counter/
├── pico-battery-counter/    # MicroPython code for Raspberry Pi Pico W
│   ├── main.py              # Main program loop
│   ├── config.py            # Configuration (WiFi, API endpoints, pins)
│   ├── sensor.py            # IR sensor handler
│   ├── sync.py              # WiFi and API sync functions
│   └── tft.py               # TFT display driver wrapper
├── api/                     # Node.js Express API
│   ├── index.js             # API server entry point
│   ├── routes.js            # API route definitions
│   ├── config.js            # Supabase client and constants
│   ├── package.json         # Node dependencies
│   ├── routes/
│   │   ├── log.js           # Battery logging endpoints
│   │   └── stats.js         # Statistics endpoint
│   └── tests/               # Python API tests
│       ├── test_log.py
│       ├── test_logs.py
│       ├── test_stats.py
│       └── runner.py
├── dashboard/               # React/Vite Web Dashboard
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── pages/
│   │   │   ├── Index.tsx    # Dashboard home page
│   │   │   └── NotFound.tsx # 404 page
│   │   └── components/      # UI components
│   │       ├── BatteryChart.tsx    # Data visualization chart
│   │       ├── DashboardHeader.tsx # Header component
│   │       ├── StatCard.tsx        # Statistic display cards
│   │       └── ui/                 # shadcn/ui components
│   ├── vite.config.ts       # Vite configuration
│   ├── tailwind.config.ts   # Tailwind CSS configuration
│   └── package.json         # Frontend dependencies
└── schema.sql               # Supabase database schema
```

## Features

- **IR Sensor Detection**: Detects batteries passing through with debouncing
- **Local Caching**: Stores counts locally when offline
- **Cloud Sync**: Automatically syncs data to a remote API
- **Statistics**: Tracks total batteries and calculates environmental impact (soil/water saved)
- **TFT Display**: Shows real-time count on connected display
- **Web Dashboard**: Interactive React-based dashboard with real-time statistics and data visualization
- **Data Visualization**: Chart displaying battery collection trends over time
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
   API_LOG = "https://your-api.vercel.app/log"
   API_STATS = "https://your-api.vercel.app/stats"
   IR_PIN = 15  # GPIO pin for IR sensor
   DEVICE_ID = "pico_w_1"  # Unique identifier for this device
   ```

3. Upload all files in `pico-battery-counter/` to your Pico W
4. Connect the IR sensor to the configured GPIO pin (default: GPIO 15)
5. Connect LED indicator to GPIO 2
6. (Optional) Initialize TFT display in `main.py` - uncomment and configure the TFT initialization section

### 2. API Setup

1. Create a Supabase project and database

2. Run the SQL schema from `schema.sql` in your Supabase SQL Editor to create the `battery_logs` table

3. Install dependencies:

   ```bash
   cd api
   npm install
   ```

4. Create `.env` file:

   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

   **Note:** For production, consider using `SUPABASE_SERVICE_ROLE_KEY` instead of `SUPABASE_ANON_KEY` to bypass Row Level Security (RLS)

5. Run the server:

   ```bash
   npm start        # Production
   npm run dev      # Development with auto-reload
   ```

6. Deploy to Vercel or your preferred platform

### 3. Dashboard Setup

1. Navigate to the dashboard directory:

   ```bash
   cd dashboard
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Create `.env` file (or `.env.local`):

   ```env
   VITE_API_BASE_URL=https://your-api.vercel.app
   ```

   For local development, use:

   ```env
   VITE_API_BASE_URL=http://localhost:3000
   ```

4. Run the development server:

   ```bash
   npm run dev
   ```

5. Build for production:

   ```bash
   npm run build
   ```

6. Preview production build:

   ```bash
   npm run preview
   ```

The dashboard displays:

- **Total Batteries Collected**: Real-time count of all batteries logged
- **Soil Saved**: Environmental impact in kilograms
- **Water Saved**: Environmental impact in liters
- **Collection Chart**: Visual timeline of battery collection data

### 4. Testing the API

Python tests are available in the `api/tests/` directory:

```bash
cd api/tests
python runner.py
```

## API Endpoints

### GET `/`

Root endpoint - returns API status

**Response:** `Battery Counter API`

### POST `/log`

Log a battery count event

**Request body:**

```json
{
  "timestamp": 1234567890,
  "amount": 1,
  "device_id": "pico_w_1"
}
```

**Response:**

```json
{
  "ok": true
}
```

**Note:** `timestamp` is in Unix epoch seconds (will be converted to timestamptz)

### GET `/log`

Retrieve all battery logs (ordered by timestamp, descending)

**Response:**

```json
[
  {
    "id": 1,
    "timestamp": "2025-11-17T10:30:00Z",
    "amount": 1,
    "device_id": "pico_w_1",
    "created_at": "2025-11-17T10:30:01Z"
  }
]
```

### GET `/stats`

Get aggregate statistics

**Response:**

```json
{
  "total": 150,
  "soil": 3.0,
  "water": 22.5
}
```

## Environmental Impact Calculation

The system calculates environmental benefits based on battery recycling:

- **Soil saved**: 0.02 kg per battery (20 grams)
- **Water saved**: 0.15 L per battery (150 milliliters)

These constants are configured in `api/config.js` as `SOIL_PER_BATTERY` and `WATER_PER_BATTERY`.

## How It Works

1. **Detection**: IR sensor detects battery passing through (with debouncing to prevent double-counts)
2. **Local Storage**: Count is stored locally in `cache.json` on the Pico W
3. **Sync**: Pico W connects to WiFi and syncs cached data to API with device_id
4. **Database**: API stores data in Supabase `battery_logs` table with timestamp, amount, and device_id
5. **Statistics**: Server calculates total batteries and environmental impact
6. **Display**: Statistics are fetched and displayed on TFT screen (total = server total + unsynced local count)
7. **Feedback**: LED on GPIO 2 blinks during each main loop iteration to indicate activity

## Database Schema

The `battery_logs` table structure:

| Column       | Type        | Description                           |
| ------------ | ----------- | ------------------------------------- |
| `id`         | bigint      | Auto-incrementing primary key         |
| `timestamp`  | timestamptz | When the battery was logged           |
| `amount`     | int         | Number of batteries (default: 1)      |
| `device_id`  | text        | Unique identifier for the Pico device |
| `created_at` | timestamptz | Record creation time (auto-generated) |

Indexes are created on `timestamp` and `device_id` for optimized queries.

## License

ISC

## Author

Quang Ngo
