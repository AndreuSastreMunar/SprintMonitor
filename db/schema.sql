-- Sprint Monitor MVP
-- Ejecutar en Supabase > SQL Editor
-- IMPORTANTE: usa solo la ANON KEY en Streamlit. Nunca expongas la service_role key.

create extension if not exists pgcrypto;

create type public.user_role as enum ('athlete', 'coach');
create type public.sex_type as enum ('male', 'female');
create type public.event_type as enum ('100m', '200m', '4x100', 'other');

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  full_name text not null default '',
  role public.user_role not null default 'athlete',
  sex public.sex_type,
  birth_date date,
  specialty text,
  coach_id uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now()
);

create table public.training_sessions (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  session_date date not null default current_date,
  duration_minutes integer check (duration_minutes > 0),
  rpe numeric(3,1) check (rpe >= 0 and rpe <= 10),
  srpe_load numeric generated always as (
    case when duration_minutes is not null and rpe is not null
      then duration_minutes * rpe else null end
  ) stored,
  notes text,
  created_at timestamptz not null default now()
);

create table public.sprint_sets (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.training_sessions(id) on delete cascade,
  set_order integer not null default 1,
  distance_m numeric(6,2) not null check (distance_m > 0),
  repetitions integer not null check (repetitions > 0 and repetitions <= 50),
  recovery_seconds integer check (recovery_seconds >= 0),
  created_at timestamptz not null default now()
);

create table public.sprint_reps (
  id uuid primary key default gen_random_uuid(),
  sprint_set_id uuid not null references public.sprint_sets(id) on delete cascade,
  rep_number integer not null check (rep_number > 0),
  time_seconds numeric(7,3) check (time_seconds > 0),
  created_at timestamptz not null default now(),
  unique(sprint_set_id, rep_number)
);

create table public.competitions (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  competition_date date not null,
  competition_name text not null,
  venue text,
  event public.event_type not null,
  round text,
  lane integer check (lane between 1 and 9),
  reaction_time numeric(5,3) check (reaction_time > 0),
  result_seconds numeric(7,3) not null check (result_seconds > 0),
  wind numeric(4,2),
  position integer check (position > 0),
  notes text,
  created_at timestamptz not null default now()
);

create table public.menstrual_cycles (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.profiles(id) on delete cascade,
  start_date date not null,
  end_date date,
  share_with_coach boolean not null default false,
  notes text,
  created_at timestamptz not null default now(),
  check (end_date is null or end_date >= start_date)
);

create index training_sessions_athlete_date_idx
on public.training_sessions(athlete_id, session_date desc);

create index competitions_athlete_date_idx
on public.competitions(athlete_id, competition_date desc);

create index menstrual_cycles_athlete_date_idx
on public.menstrual_cycles(athlete_id, start_date desc);

-- Crear perfil automáticamente al registrar un usuario.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', '')
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();

-- Helper: ¿el usuario actual es entrenador?
create or replace function public.is_coach()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles
    where id = (select auth.uid()) and role = 'coach'
  );
$$;

-- Helper: ¿es el entrenador asignado a ese atleta?
create or replace function public.is_assigned_coach(target_athlete uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.profiles p
    where p.id = target_athlete
      and p.coach_id = (select auth.uid())
      and public.is_coach()
  );
$$;

alter table public.profiles enable row level security;
alter table public.training_sessions enable row level security;
alter table public.sprint_sets enable row level security;
alter table public.sprint_reps enable row level security;
alter table public.competitions enable row level security;
alter table public.menstrual_cycles enable row level security;

-- PROFILES
create policy "profile_self_select"
on public.profiles for select to authenticated
using ((select auth.uid()) = id);

create policy "coach_select_assigned_profiles"
on public.profiles for select to authenticated
using (coach_id = (select auth.uid()) and public.is_coach());

create policy "profile_self_update"
on public.profiles for update to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

-- Limita qué columnas puede modificar un usuario desde la API.
-- role y coach_id quedan fuera: se administran desde Supabase por el responsable.
revoke update on public.profiles from authenticated;
grant update (full_name, sex, birth_date, specialty) on public.profiles to authenticated;

-- TRAINING SESSIONS
create policy "athlete_own_sessions_all"
on public.training_sessions for all to authenticated
using (athlete_id = (select auth.uid()))
with check (athlete_id = (select auth.uid()));

create policy "coach_read_assigned_sessions"
on public.training_sessions for select to authenticated
using (public.is_assigned_coach(athlete_id));

-- SPRINT SETS
create policy "athlete_own_sprint_sets_all"
on public.sprint_sets for all to authenticated
using (
  exists (
    select 1 from public.training_sessions ts
    where ts.id = session_id and ts.athlete_id = (select auth.uid())
  )
)
with check (
  exists (
    select 1 from public.training_sessions ts
    where ts.id = session_id and ts.athlete_id = (select auth.uid())
  )
);

create policy "coach_read_assigned_sprint_sets"
on public.sprint_sets for select to authenticated
using (
  exists (
    select 1 from public.training_sessions ts
    where ts.id = session_id
      and public.is_assigned_coach(ts.athlete_id)
  )
);

-- SPRINT REPS
create policy "athlete_own_sprint_reps_all"
on public.sprint_reps for all to authenticated
using (
  exists (
    select 1
    from public.sprint_sets ss
    join public.training_sessions ts on ts.id = ss.session_id
    where ss.id = sprint_set_id
      and ts.athlete_id = (select auth.uid())
  )
)
with check (
  exists (
    select 1
    from public.sprint_sets ss
    join public.training_sessions ts on ts.id = ss.session_id
    where ss.id = sprint_set_id
      and ts.athlete_id = (select auth.uid())
  )
);

create policy "coach_read_assigned_sprint_reps"
on public.sprint_reps for select to authenticated
using (
  exists (
    select 1
    from public.sprint_sets ss
    join public.training_sessions ts on ts.id = ss.session_id
    where ss.id = sprint_set_id
      and public.is_assigned_coach(ts.athlete_id)
  )
);

-- COMPETITIONS
create policy "athlete_own_competitions_all"
on public.competitions for all to authenticated
using (athlete_id = (select auth.uid()))
with check (athlete_id = (select auth.uid()));

create policy "coach_read_assigned_competitions"
on public.competitions for select to authenticated
using (public.is_assigned_coach(athlete_id));

-- MENSTRUAL: atleta siempre. Entrenador solo si la atleta marca compartir.
create policy "athlete_own_cycles_all"
on public.menstrual_cycles for all to authenticated
using (athlete_id = (select auth.uid()))
with check (athlete_id = (select auth.uid()));

create policy "coach_read_shared_cycles"
on public.menstrual_cycles for select to authenticated
using (
  share_with_coach = true
  and public.is_assigned_coach(athlete_id)
);
