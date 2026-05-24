create table if not exists causal_events (
  id uuid primary key default gen_random_uuid(),
  event_date date not null,
  event_name text not null,
  event_type text not null check (event_type in ('product_launch','campaign','tournament','press_release','crisis','partnership')),
  description text,
  platform text not null default 'all',
  created_at timestamptz not null default now()
);

insert into causal_events (event_date, event_name, event_type, description, platform) values
  ('2025-01-01', 'Q1 2025 Campaign Start', 'campaign', 'New year marketing push', 'all'),
  ('2025-03-01', 'Ben Johns Partnership Renewed', 'partnership', 'Multi-year contract extension announcement', 'all'),
  ('2025-06-01', 'Hyperion CFS Launch', 'product_launch', 'Hyperion Carbon Fiber Surface paddle launch', 'all'),
  ('2024-10-01', 'US Open Pickleball 2024', 'tournament', 'JOOLA sponsor at US Open Pickleball Championships', 'all')
on conflict do nothing;
