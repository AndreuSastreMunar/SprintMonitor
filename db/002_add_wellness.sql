create table if not exists public.wellness_entries (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  entry_date date not null default current_date,
  sleep integer not null check (sleep between 1 and 5),
  fatigue integer not null check (fatigue between 1 and 5),
  muscle_soreness integer not null check (muscle_soreness between 1 and 5),
  stress integer not null check (stress between 1 and 5),
  readiness integer not null check (readiness between 1 and 5),
  notes text,
  created_at timestamptz not null default now(),
  unique (athlete_id, entry_date)
);

alter table public.wellness_entries enable row level security;

create policy "athlete_own_wellness_all"
on public.wellness_entries for all to authenticated
using (athlete_id = auth.uid())
with check (athlete_id = auth.uid());

create policy "coach_read_assigned_wellness"
on public.wellness_entries for select to authenticated
using (public.is_assigned_coach(athlete_id));
