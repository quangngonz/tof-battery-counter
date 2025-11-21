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
-- Allow public read access for dashboard (anon key)
create policy "Allow public read access"
on public.battery_logs
for select
to anon, authenticated
using (true);

-- Allow inserts from service role (API server)
create policy "Allow service role inserts"
on public.battery_logs
for insert
to service_role
using (true);

-- ============================================================
-- Enable Realtime
-- ============================================================
-- Enable realtime for the battery_logs table
alter publication supabase_realtime add table battery_logs;

-- ============================================================
-- Notes
-- ============================================================
-- 1. Use SUPABASE_SERVICE_ROLE_KEY (not ANON_KEY) in production
--    for server-side operations to bypass RLS
-- 2. The timestamp field expects Unix timestamps converted to timestamptz
-- 3. Default amount is 1 (one battery per event)
-- 4. device_id helps track multiple Pico W devices if needed
