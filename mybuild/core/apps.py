from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):  # type: ignore[override]
        # Import RBAC signal handlers
        try:
            from . import rbac  # noqa: F401
        except Exception:
            # Fail silently to not break migrations in edge cases
            pass
