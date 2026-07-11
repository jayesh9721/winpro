-- CampaignIQ — analysis_history table
-- Run this once in the Supabase Dashboard: SQL Editor > New query > paste > Run
-- (project izqmcfreeyommcjfzqeh)

create extension if not exists pgcrypto;

create table if not exists public.analysis_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  filename text,
  kpis jsonb not null,
  campaign_data jsonb not null,
  ai_brief text,
  ai_anomaly text,
  ai_recs text,
  ai_forecast text,
  ai_bench text
);

alter table public.analysis_history enable row level security;

create policy "Users can view own history"
  on public.analysis_history for select
  using (auth.uid() = user_id);

create policy "Users can insert own history"
  on public.analysis_history for insert
  with check (auth.uid() = user_id);

create policy "Users can delete own history"
  on public.analysis_history for delete
  using (auth.uid() = user_id);

create index if not exists analysis_history_user_id_idx on public.analysis_history (user_id, created_at desc);
