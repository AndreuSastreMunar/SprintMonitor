-- 003_load_meters_rpe.sql
-- Cambia la carga de duración x RPE a metros totales x RPE.
-- Ejecutar una sola vez en Supabase > SQL Editor.

alter table public.training_sessions
add column if not exists volume_m numeric(10,2);

-- Recupera el volumen de sesiones ya existentes a partir de los bloques de sprint.
update public.training_sessions ts
set volume_m = v.total_m
from (
  select session_id, sum(distance_m * repetitions)::numeric(10,2) as total_m
  from public.sprint_sets
  group by session_id
) v
where ts.id = v.session_id;

-- srpe_load se conserva como nombre interno para no romper versiones anteriores
-- de la app, pero desde esta migración significa: metros x RPE.
alter table public.training_sessions
drop column if exists srpe_load;

alter table public.training_sessions
add column srpe_load numeric generated always as (
  case
    when volume_m is not null and rpe is not null then volume_m * rpe
    else null
  end
) stored;

-- Mantiene volume_m sincronizado si se añade, modifica o elimina un bloque.
create or replace function public.refresh_training_session_volume()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  target_session uuid;
begin
  target_session := coalesce(new.session_id, old.session_id);

  update public.training_sessions ts
  set volume_m = coalesce((
    select sum(ss.distance_m * ss.repetitions)::numeric(10,2)
    from public.sprint_sets ss
    where ss.session_id = target_session
  ), 0)
  where ts.id = target_session;

  return coalesce(new, old);
end;
$$;

drop trigger if exists sprint_sets_refresh_session_volume on public.sprint_sets;
create trigger sprint_sets_refresh_session_volume
after insert or update or delete on public.sprint_sets
for each row execute procedure public.refresh_training_session_volume();
