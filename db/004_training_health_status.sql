-- Estado de salud al finalizar cada entrenamiento
-- Ejecutar en Supabase > SQL Editor

alter table public.training_sessions
add column if not exists health_status text;

alter table public.training_sessions
drop constraint if exists training_sessions_health_status_check;

alter table public.training_sessions
add constraint training_sessions_health_status_check
check (
  health_status is null
  or health_status in (
    'completed_no_problem',
    'completed_with_health_problem',
    'adapted_due_health_problem',
    'not_completed_due_health_problem'
  )
);

comment on column public.training_sessions.health_status is
'Estado de salud al finalizar la sesión: completed_no_problem, completed_with_health_problem, adapted_due_health_problem o not_completed_due_health_problem.';
