create table if not exists joola_timeseries_weekly (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid not null,
  week_start date not null,
  platform text not null,
  metric_name text not null,
  value float not null default 0,
  row_count int not null default 1,
  source_table text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(brand_id, week_start, platform, metric_name)
);

create index if not exists idx_jtw_brand_week on joola_timeseries_weekly(brand_id, week_start);
create index if not exists idx_jtw_platform_metric on joola_timeseries_weekly(platform, metric_name);

create table if not exists joola_timeseries_daily (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid not null,
  metric_date_local date not null,
  platform text not null,
  metric_name text not null,
  value float not null default 0,
  source_table text not null,
  created_at timestamptz not null default now(),
  unique(brand_id, metric_date_local, platform, metric_name)
);

create index if not exists idx_jtd_brand_date on joola_timeseries_daily(brand_id, metric_date_local);
