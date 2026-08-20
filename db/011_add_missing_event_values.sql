-- Añade las pruebas que la app ya ofrece pero que faltaban en el enum event_type.
-- Ejecutar una sola vez en Supabase > SQL Editor.

alter type public.event_type add value if not exists '60m';
alter type public.event_type add value if not exists '400m';
