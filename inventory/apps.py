from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"

    def ready(self):
        # Import signal handlers to activate business-logic hooks
        # Avoid circular-import issues by importing inside the method.
        from . import signals  # noqa: F401
