-- Añade el registro obligatorio de gimnasio y pliometría a cada entrenamiento.
-- Ejecutar en Supabase > SQL Editor una sola vez.

alter table public.training_sessions
  add column if not exists did_gym boolean,
  add column if not exists did_plyometrics boolean;

comment on column public.training_sessions.did_gym is
  'Indica si el atleta realizó gimnasio en esta sesión.';

comment on column public.training_sessions.did_plyometrics is
  'Indica si el atleta realizó pliometría en esta sesión.';
