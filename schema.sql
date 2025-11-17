-- ============================================================
-- Battery Counter - Supabase Database Schema
-- ============================================================
-- This file contains the SQL schema for the battery_logs table
-- Run this in your Supabase SQL Editor to set up the database
-- ============================================================

-- Create the battery_logs table
create table public.battery_logs (
  id bigint generated always as identity primary key,
  timestamp timestamptz not null,
  amount int not null default 1,
  device_id text not null,

  -- Optional, but helps Supabase dashboard
  created_at timestamptz not null default now()
);

-- Optional indexes for faster stats queries
create index battery_logs_timestamp_idx on public.battery_logs (timestamp);
create index battery_logs_device_idx on public.battery_logs (device_id);

-- ============================================================
-- Row Level Security (RLS)
-- ============================================================
-- Supabase enables RLS by default, but ensure it's on:
alter table public.battery_logs enable row level security;

-- ============================================================
-- Security Policies
-- ============================================================
-- If your Express server uses the SERVICE_ROLE_KEY, it bypasses RLS.
-- You don't need extra policies in that case.
--
-- Optional: Policy for device-level insert access
-- (Uncomment if you want explicit policy control)
--
-- create policy "Allow inserts from service role"
-- on public.battery_logs
-- for insert
-- to service_role
-- using (true);

-- ============================================================
-- Notes
-- ============================================================
-- 1. Use SUPABASE_SERVICE_ROLE_KEY (not ANON_KEY) in production
--    for server-side operations to bypass RLS
-- 2. The timestamp field expects Unix timestamps converted to timestamptz
-- 3. Default amount is 1 (one battery per event)
-- 4. device_id helps track multiple Pico W devices if needed
