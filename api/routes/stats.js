import { supabase, SOIL_PER_BATTERY, WATER_PER_BATTERY } from '../config.js';

export const getStats = async (req, res) => {
  const { data, error } = await supabase.from('battery_logs').select('amount');

  if (error) return res.status(500).json({ error });

  const total = data.reduce((s, r) => s + r.amount, 0);

  res.json({
    total,
    soil: total * SOIL_PER_BATTERY,
    water: total * WATER_PER_BATTERY,
  });
};
