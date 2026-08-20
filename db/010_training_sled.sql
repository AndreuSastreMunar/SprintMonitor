alter table public.training_sessions
add column if not exists did_sled boolean;

comment on column public.training_sessions.did_sled is
'Indica si el atleta realizó series con arrastres en la sesión.';
