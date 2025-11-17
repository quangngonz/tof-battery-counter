import { supabase, SOIL_PER_BATTERY, WATER_PER_BATTERY } from '../config.js';

export const getStats = async (req, res) => {
  const { data, error } = await supabase.from('battery_logs').select('amount');

  if (error) {
    console.error('Database error:', error);
    return res.status(500).json({ error: 'Failed to fetch stats' });
  }

  const total = data.reduce((sum, record) => sum + (record.amount || 0), 0);

  res.json({
    total,
    soil: Math.round(total * SOIL_PER_BATTERY * 100) / 100,
    water: Math.round(total * WATER_PER_BATTERY * 100) / 100,
  });
};
