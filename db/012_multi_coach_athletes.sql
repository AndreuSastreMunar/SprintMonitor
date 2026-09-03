-- Permite que un mismo atleta esté vinculado a varios entrenadores.
-- Ejecutar una sola vez en Supabase > SQL Editor.

create table if not exists public.coach_athletes (
  coach_id uuid not null references public.profiles(id) on delete cascade,
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (coach_id, athlete_id),
  check (coach_id <> athlete_id)
);

create index if not exists coach_athletes_athlete_idx
  on public.coach_athletes (athlete_id);

-- Conserva automáticamente las asignaciones actuales hechas con profiles.coach_id.
insert into public.coach_athletes (coach_id, athlete_id)
select coach_id, id
from public.profiles
where coach_id is not null
on conflict (coach_id, athlete_id) do nothing;

alter table public.coach_athletes enable row level security;

drop policy if exists "coach_read_own_athlete_links" on public.coach_athletes;
create policy "coach_read_own_athlete_links"
on public.coach_athletes for select to authenticated
using (coach_id = auth.uid());

drop policy if exists "athlete_read_own_coach_links" on public.coach_athletes;
create policy "athlete_read_own_coach_links"
on public.coach_athletes for select to authenticated
using (athlete_id = auth.uid());

-- Esta función ya se usa en las políticas RLS de entrenamiento, wellness, etc.
-- La redefinimos para aceptar tanto la nueva tabla como el coach_id antiguo.
create or replace function public.is_assigned_coach(target_athlete_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.coach_athletes ca
    where ca.athlete_id = target_athlete_id
      and ca.coach_id = auth.uid()
  )
  or exists (
    select 1
    from public.profiles p
    where p.id = target_athlete_id
      and p.coach_id = auth.uid()
  );
$$;

revoke all on function public.is_assigned_coach(uuid) from public;
grant execute on function public.is_assigned_coach(uuid) to authenticated;

-- Los entrenadores vinculados pueden ver el perfil del atleta.
drop policy if exists "multi_coach_read_linked_profiles" on public.profiles;
create policy "multi_coach_read_linked_profiles"
on public.profiles for select to authenticated
using (
  id = auth.uid()
  or exists (
    select 1 from public.coach_athletes ca
    where ca.athlete_id = profiles.id
      and ca.coach_id = auth.uid()
  )
);

-- Políticas adicionales de lectura. Las políticas RLS se combinan con OR,
-- por lo que no eliminan las reglas existentes del atleta ni del entrenador principal.
drop policy if exists "multi_coach_read_training_sessions" on public.training_sessions;
create policy "multi_coach_read_training_sessions"
on public.training_sessions for select to authenticated
using (public.is_assigned_coach(athlete_id));

drop policy if exists "multi_coach_read_wellness" on public.wellness_entries;
create policy "multi_coach_read_wellness"
on public.wellness_entries for select to authenticated
using (public.is_assigned_coach(athlete_id));

drop policy if exists "multi_coach_read_competitions" on public.competitions;
create policy "multi_coach_read_competitions"
on public.competitions for select to authenticated
using (public.is_assigned_coach(athlete_id));

drop policy if exists "multi_coach_read_cycles" on public.menstrual_cycles;
create policy "multi_coach_read_cycles"
on public.menstrual_cycles for select to authenticated
using (share_with_coach = true and public.is_assigned_coach(athlete_id));

drop policy if exists "multi_coach_read_marks" on public.athlete_marks;
create policy "multi_coach_read_marks"
on public.athlete_marks for select to authenticated
using (public.is_assigned_coach(athlete_id));

-- Series y repeticiones dependen de la sesión del atleta.
drop policy if exists "multi_coach_read_sprint_sets" on public.sprint_sets;
create policy "multi_coach_read_sprint_sets"
on public.sprint_sets for select to authenticated
using (
  exists (
    select 1 from public.training_sessions ts
    where ts.id = sprint_sets.session_id
      and public.is_assigned_coach(ts.athlete_id)
  )
);

drop policy if exists "multi_coach_read_sprint_reps" on public.sprint_reps;
create policy "multi_coach_read_sprint_reps"
on public.sprint_reps for select to authenticated
using (
  exists (
    select 1
    from public.sprint_sets ss
    join public.training_sessions ts on ts.id = ss.session_id
    where ss.id = sprint_reps.sprint_set_id
      and public.is_assigned_coach(ts.athlete_id)
  )
);
