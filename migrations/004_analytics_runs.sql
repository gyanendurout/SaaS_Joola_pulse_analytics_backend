create table if not exists analytics_runs (
  id uuid primary key default gen_random_uuid(),
  run_type text not null,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  status text not null default 'running' check (status in ('running','completed','failed')),
  rows_processed int not null default 0,
  error_message text,
  triggered_by text not null default 'scheduler' check (triggered_by in ('scheduler','webhook','manual'))
);

create index if not exists idx_runs_status on analytics_runs(status, started_at desc);
