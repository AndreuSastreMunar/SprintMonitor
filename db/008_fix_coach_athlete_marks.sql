-- Corrige el acceso del entrenador asignado a las marcas manuales de sus atletas.
-- Ejecutar una sola vez en Supabase > SQL Editor.

-- Asegura privilegios de tabla para usuarios autenticados.
grant select, insert, update, delete on public.athlete_marks to authenticated;

-- Reemplaza la política de lectura del entrenador por el helper SECURITY DEFINER
-- ya usado en el resto del esquema para evitar problemas de RLS encadenada.
drop policy if exists "coach_select_assigned_athlete_marks" on public.athlete_marks;
create policy "coach_select_assigned_athlete_marks"
on public.athlete_marks for select to authenticated
using (public.is_assigned_coach(athlete_id));
