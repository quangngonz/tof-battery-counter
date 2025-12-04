import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

export const SOIL_PER_BATTERY = 1; // in meter square
export const WATER_PER_BATTERY = 500; // in L
