-- Mark pre-migration rows as legacy so old simulator values are never shown as live hardware.
alter table public.sensor_readings
  add column if not exists source text not null default 'legacy';

create index if not exists sensor_readings_user_source_created_idx
  on public.sensor_readings(user_id, source, created_at desc);
