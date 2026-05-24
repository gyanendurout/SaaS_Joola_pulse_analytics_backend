create table if not exists correlation_results (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references analytics_runs(id),
  brand_id uuid not null,
  metric_a text not null,
  metric_b text not null,
  pearson_r float,
  spearman_r float,
  p_value float,
  n_weeks int not null,
  window_weeks int not null,
  ai_narrative text,
  created_at timestamptz not null default now()
);

create table if not exists granger_results (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references analytics_runs(id),
  brand_id uuid not null,
  cause_metric text not null,
  effect_metric text not null,
  max_lag_weeks int not null,
  optimal_lag int,
  f_stat float,
  p_value float,
  is_significant boolean not null default false,
  ai_narrative text,
  created_at timestamptz not null default now()
);

create table if not exists changepoint_results (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references analytics_runs(id),
  brand_id uuid not null,
  metric text not null,
  changepoint_week date not null,
  confidence float,
  pre_mean float,
  post_mean float,
  pct_change float,
  direction text check (direction in ('increase','decrease')),
  ai_label text,
  created_at timestamptz not null default now()
);

create table if not exists its_results (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references analytics_runs(id),
  brand_id uuid not null,
  event_id uuid references causal_events(id),
  metric text not null,
  pre_slope float,
  post_slope float,
  level_change float,
  trend_change float,
  p_value float,
  is_significant boolean not null default false,
  r_squared float,
  ai_narrative text,
  created_at timestamptz not null default now()
);

create table if not exists composite_scores_weekly (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid not null,
  week_start date not null,
  attention_score float not null default 0,
  sales_likelihood_score float not null default 0,
  attention_components jsonb,
  sales_components jsonb,
  ai_narrative text,
  created_at timestamptz not null default now(),
  unique(brand_id, week_start)
);

create index if not exists idx_composite_brand_week on composite_scores_weekly(brand_id, week_start desc);

create table if not exists forecast_results (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references analytics_runs(id),
  brand_id uuid not null,
  metric text not null,
  forecast_week date not null,
  yhat float,
  yhat_lower float,
  yhat_upper float,
  model text not null default 'linear',
  horizon_weeks int not null,
  created_at timestamptz not null default now()
);

create table if not exists ai_narratives (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid not null,
  week_start date not null,
  narrative_type text not null default 'weekly_summary'
    check (narrative_type in ('weekly_summary','crisis_alert','opportunity_signal')),
  title text not null,
  body text not null,
  key_points jsonb,
  model_used text,
  tokens_used int,
  created_at timestamptz not null default now(),
  unique(brand_id, week_start, narrative_type)
);
