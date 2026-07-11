-- CampaignIQ — add chat transcript storage to saved history
-- Run this once in the Supabase Dashboard: SQL Editor > New query > paste > Run

alter table public.analysis_history
  add column if not exists chat_transcript jsonb;
