import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

export const SOIL_PER_BATTERY = 0.02;
export const WATER_PER_BATTERY = 0.15;
