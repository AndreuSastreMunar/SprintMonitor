-- Gestión de atletas desde la propia app del entrenador.
-- Ejecutar una sola vez en Supabase > SQL Editor después de 012_multi_coach_athletes.sql.

-- Desde esta migración, la relación válida entrenador-atleta es coach_athletes.
-- Conservamos profiles.coach_id solo como dato legado, pero ya no concede acceso por sí solo.
create or replace function public.is_assigned_coach(target_athlete uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select public.is_coach()
  and exists (
    select 1
    from public.coach_athletes ca
    where ca.athlete_id = target_athlete
      and ca.coach_id = auth.uid()
  );
$$;

revoke all on function public.is_assigned_coach(uuid) from public;
grant execute on function public.is_assigned_coach(uuid) to authenticated;

-- Evita que la antigua columna profiles.coach_id siga dando acceso después de quitar una relación.
drop policy if exists "coach_select_assigned_profiles" on public.profiles;

-- Lista únicamente los atletas vinculados al entrenador autenticado.
drop function if exists public.coach_my_athletes();
create function public.coach_my_athletes()
returns table (
  id uuid,
  full_name text,
  email text,
  specialty text,
  sex public.sex_type
)
language sql
stable
security definer
set search_path = public
as $$
  select p.id, p.full_name, p.email, p.specialty, p.sex
  from public.coach_athletes ca
  join public.profiles p on p.id = ca.athlete_id
  where ca.coach_id = auth.uid()
    and public.is_coach()
  order by coalesce(nullif(p.full_name,''), p.email);
$$;

-- Añade un atleta buscando por su email exacto. No expone un listado global de deportistas.
drop function if exists public.coach_add_athlete_by_email(text);
create function public.coach_add_athlete_by_email(athlete_email text)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  target_id uuid;
begin
  if not public.is_coach() then
    raise exception 'Solo los entrenadores pueden gestionar atletas';
  end if;

  select p.id into target_id
  from public.profiles p
  where lower(trim(p.email)) = lower(trim(athlete_email))
    and p.role = 'athlete'
  limit 1;

  if target_id is null then
    raise exception 'No se encontró ningún atleta con ese email';
  end if;

  if target_id = auth.uid() then
    raise exception 'No puedes asignarte a ti mismo';
  end if;

  insert into public.coach_athletes (coach_id, athlete_id)
  values (auth.uid(), target_id)
  on conflict (coach_id, athlete_id) do nothing;

  return target_id;
end;
$$;

-- Quita únicamente la relación del entrenador autenticado con ese atleta.
drop function if exists public.coach_remove_athlete(uuid);
create function public.coach_remove_athlete(athlete_uuid uuid)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  removed_count integer;
begin
  if not public.is_coach() then
    raise exception 'Solo los entrenadores pueden gestionar atletas';
  end if;

  delete from public.coach_athletes
  where coach_id = auth.uid()
    and athlete_id = athlete_uuid;

  get diagnostics removed_count = row_count;
  return removed_count > 0;
end;
$$;

revoke all on function public.coach_my_athletes() from public;
revoke all on function public.coach_add_athlete_by_email(text) from public;
revoke all on function public.coach_remove_athlete(uuid) from public;
grant execute on function public.coach_my_athletes() to authenticated;
grant execute on function public.coach_add_athlete_by_email(text) to authenticated;
grant execute on function public.coach_remove_athlete(uuid) to authenticated;
