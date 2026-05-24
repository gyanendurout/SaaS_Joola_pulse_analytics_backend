-- Drop and recreate so the schema is always correct (idempotent)
drop table if exists product_aliases cascade;

create table product_aliases (
  id uuid primary key default gen_random_uuid(),
  canonical_name text not null,
  alias text not null,
  platform text not null default 'all',
  confidence float not null default 1.0,
  created_at timestamptz not null default now(),
  unique(alias, platform)
);

insert into product_aliases (canonical_name, alias, platform) values
  ('Hyperion', 'hyperion', 'all'),
  ('Hyperion', 'ben johns hyperion', 'all'),
  ('Hyperion', 'joola hyperion', 'all'),
  ('Perseus', 'perseus', 'all'),
  ('Perseus', 'joola perseus', 'all'),
  ('Scorpeus', 'scorpeus', 'all'),
  ('Scorpeus', 'joola scorpeus', 'all'),
  ('Vivid', 'vivid', 'all'),
  ('Vivid', 'joola vivid', 'all')
on conflict (alias, platform) do nothing;
