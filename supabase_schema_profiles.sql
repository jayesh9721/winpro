-- CampaignIQ — business_profiles table (persona system)
-- Run this once in the Supabase Dashboard: SQL Editor > New query > paste > Run
-- (project izqmcfreeyommcjfzqeh)
-- Assumes supabase_schema.sql has already been run (analysis_history exists).

create table if not exists public.business_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  description text,
  goal text not null,              -- 'leads' | 'awareness' | 'traffic' | 'sales' | 'engagement'
  target_value text,               -- free text, e.g. "CPL <= Rs.500" or "ROAS >= 4x"
  industry text,
  monthly_budget numeric,
  system_prompt text,              -- AI-generated personalized system prompt for this profile
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.business_profiles enable row level security;

create policy "Users can view own profiles"
  on public.business_profiles for select
  using (auth.uid() = user_id);

create policy "Users can insert own profiles"
  on public.business_profiles for insert
  with check (auth.uid() = user_id);

create policy "Users can update own profiles"
  on public.business_profiles for update
  using (auth.uid() = user_id);

create policy "Users can delete own profiles"
  on public.business_profiles for delete
  using (auth.uid() = user_id);

create index if not exists business_profiles_user_id_idx on public.business_profiles (user_id, created_at desc);

-- Scope saved reports to a profile too
alter table public.analysis_history
  add column if not exists profile_id uuid references public.business_profiles(id) on delete cascade;

create index if not exists analysis_history_profile_id_idx on public.analysis_history (profile_id, created_at desc);
