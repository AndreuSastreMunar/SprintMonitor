-- Añade foto de perfil de atleta y un bucket privado y ligero para avatares.
-- Ejecutar una sola vez en Supabase > SQL Editor.

alter table public.profiles
  add column if not exists avatar_path text;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'profile-photos',
  'profile-photos',
  false,
  524288,
  array['image/jpeg','image/png','image/webp']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

-- El atleta puede subir/actualizar/eliminar únicamente su propia foto.
drop policy if exists "athlete_own_profile_photo_insert" on storage.objects;
create policy "athlete_own_profile_photo_insert"
on storage.objects for insert to authenticated
with check (
  bucket_id = 'profile-photos'
  and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "athlete_own_profile_photo_update" on storage.objects;
create policy "athlete_own_profile_photo_update"
on storage.objects for update to authenticated
using (
  bucket_id = 'profile-photos'
  and (storage.foldername(name))[1] = auth.uid()::text
)
with check (
  bucket_id = 'profile-photos'
  and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "athlete_own_profile_photo_delete" on storage.objects;
create policy "athlete_own_profile_photo_delete"
on storage.objects for delete to authenticated
using (
  bucket_id = 'profile-photos'
  and (storage.foldername(name))[1] = auth.uid()::text
);

-- El atleta puede leer su foto y su entrenador puede leer la de sus atletas asignados.
drop policy if exists "profile_photo_read_athlete_or_coach" on storage.objects;
create policy "profile_photo_read_athlete_or_coach"
on storage.objects for select to authenticated
using (
  bucket_id = 'profile-photos'
  and (
    (storage.foldername(name))[1] = auth.uid()::text
    or exists (
      select 1
      from public.profiles p
      where p.id::text = (storage.foldername(name))[1]
        and p.coach_id = auth.uid()
    )
  )
);
