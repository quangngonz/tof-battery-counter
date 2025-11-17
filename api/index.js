import express from 'express';
import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

const app = express();
app.use(express.json());

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

const SOIL_PER_BATTERY = 0.02;
const WATER_PER_BATTERY = 0.15;

app.get('/', (req, res) => {
  res.send('Battery Counter API');
});

// POST /log
app.post('/log', async (req, res) => {
  const { timestamp, amount, device_id } = req.body;

  if (!timestamp) {
    return res.status(400).json({ error: 'Missing timestamp' });
  }

  const { error } = await supabase.from('battery_logs').insert({
    timestamp: new Date(timestamp * 1000),
    amount: amount || 1,
    device_id: device_id || 'unknown',
  });

  if (error) return res.status(500).json({ error });

  res.json({ ok: true });
});

// GET /stats
app.get('/stats', async (req, res) => {
  const { data, error } = await supabase.from('battery_logs').select('amount');

  if (error) return res.status(500).json({ error });

  const total = data.reduce((s, r) => s + r.amount, 0);

  res.json({
    total,
    soil: total * SOIL_PER_BATTERY,
    water: total * WATER_PER_BATTERY,
  });
});

app.listen(3000, () => console.log('🚀 Server running on port 3000'));
