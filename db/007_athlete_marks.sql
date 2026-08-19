-- Registro manual de marcas del atleta (60 m, 100 m, 200 m y 400 m).
-- Ejecutar una sola vez en Supabase > SQL Editor.

create table if not exists public.athlete_marks (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  event text not null check (event in ('60m','100m','200m','400m')),
  mark_seconds numeric(8,3) not null check (mark_seconds > 0),
  mark_date date not null,
  notes text,
  created_at timestamptz not null default now()
);

create index if not exists athlete_marks_athlete_date_idx
  on public.athlete_marks (athlete_id, mark_date desc);

alter table public.athlete_marks enable row level security;

drop policy if exists "athlete_marks_select_own" on public.athlete_marks;
create policy "athlete_marks_select_own"
on public.athlete_marks for select to authenticated
using (athlete_id = auth.uid());

drop policy if exists "athlete_marks_insert_own" on public.athlete_marks;
create policy "athlete_marks_insert_own"
on public.athlete_marks for insert to authenticated
with check (athlete_id = auth.uid());

drop policy if exists "athlete_marks_update_own" on public.athlete_marks;
create policy "athlete_marks_update_own"
on public.athlete_marks for update to authenticated
using (athlete_id = auth.uid())
with check (athlete_id = auth.uid());

drop policy if exists "athlete_marks_delete_own" on public.athlete_marks;
create policy "athlete_marks_delete_own"
on public.athlete_marks for delete to authenticated
using (athlete_id = auth.uid());

drop policy if exists "coach_select_assigned_athlete_marks" on public.athlete_marks;
create policy "coach_select_assigned_athlete_marks"
on public.athlete_marks for select to authenticated
using (
  exists (
    select 1
    from public.profiles p
    where p.id = athlete_marks.athlete_id
      and p.coach_id = auth.uid()
  )
);
