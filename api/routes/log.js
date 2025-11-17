import { supabase } from '../config.js';

export const logBattery = async (req, res) => {
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
};

export const getLogs = async (req, res) => {
  const { data, error } = await supabase
    .from('battery_logs')
    .select('*')
    .order('timestamp', { ascending: false });

  if (error) return res.status(500).json({ error });

  res.json(data);
};
