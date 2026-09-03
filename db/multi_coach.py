"""Compatibilidad para que varios entrenadores puedan compartir atletas."""

from . import client as _client


class _ProfilesSelectProxy:
    def __init__(self, client, builder):
        self._client = client
        self._builder = builder

    def __getattr__(self, name):
        return getattr(self._builder, name)

    def eq(self, column, value):
        # Las vistas del entrenador existentes filtran profiles por coach_id.
        # Cuando existe la nueva tabla coach_athletes, convertimos ese filtro
        # en una consulta por los IDs de todos los atletas vinculados al coach.
        if column == "coach_id":
            try:
                links = (
                    self._client.table("coach_athletes")
                    .select("athlete_id")
                    .eq("coach_id", value)
                    .execute().data or []
                )
                athlete_ids = [row.get("athlete_id") for row in links if row.get("athlete_id")]
                if athlete_ids:
                    return self._builder.in_("id", athlete_ids)
            except Exception:
                # Si todavía no se ha ejecutado la migración SQL, mantiene
                # el comportamiento antiguo con profiles.coach_id.
                pass
        return self._builder.eq(column, value)


class _ProfilesTableProxy:
    def __init__(self, client, builder):
        self._client = client
        self._builder = builder

    def __getattr__(self, name):
        return getattr(self._builder, name)

    def select(self, *args, **kwargs):
        return _ProfilesSelectProxy(self._client, self._builder.select(*args, **kwargs))


class _MultiCoachSupabaseProxy:
    def __init__(self, client):
        self._client = client

    def __getattr__(self, name):
        return getattr(self._client, name)

    def table(self, table_name, *args, **kwargs):
        builder = self._client.table(table_name, *args, **kwargs)
        if table_name == "profiles":
            return _ProfilesTableProxy(self._client, builder)
        return builder


def install_multi_coach_support():
    if getattr(_client, "_sprint_monitor_multi_coach_installed", False):
        return

    previous_get_supabase = _client.get_supabase

    def get_supabase_multi_coach():
        return _MultiCoachSupabaseProxy(previous_get_supabase())

    _client.get_supabase = get_supabase_multi_coach
    _client._sprint_monitor_multi_coach_installed = True
