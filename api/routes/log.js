import { supabase } from '../config.js';

export const logBattery = async (req, res) => {
  const { timestamp, amount, device_id } = req.body;

  if (!timestamp) {
    return res.status(400).json({ error: 'Missing timestamp' });
  }

  if (amount && (typeof amount !== 'number' || amount < 1)) {
    return res.status(400).json({ error: 'Invalid amount' });
  }

  const { error } = await supabase.from('battery_logs').insert({
    timestamp: new Date(timestamp * 1000),
    amount: amount || 1,
    device_id: device_id || 'unknown',
  });

  if (error) {
    console.error('Database error:', error);
    return res.status(500).json({ error: 'Failed to log battery data' });
  }

  res.json({ ok: true });
};

export const getLogs = async (req, res) => {
  const { data, error } = await supabase
    .from('battery_logs')
    .select('*')
    .order('timestamp', { ascending: false });

  if (error) {
    console.error('Database error:', error);
    return res.status(500).json({ error: 'Failed to fetch logs' });
  }

  res.json(data);
};
