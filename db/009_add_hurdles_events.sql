-- Añade 60 m vallas y 110 m vallas a competiciones y marcas manuales.
-- Ejecutar una sola vez en Supabase > SQL Editor.

alter type public.event_type add value if not exists '60m vallas';
alter type public.event_type add value if not exists '110m vallas';

alter table public.athlete_marks
  drop constraint if exists athlete_marks_event_check;

alter table public.athlete_marks
  add constraint athlete_marks_event_check
  check (event in ('60m','100m','200m','400m','60m vallas','110m vallas'));
