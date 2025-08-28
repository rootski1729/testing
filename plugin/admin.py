from django.contrib import admin
from .models import Plugin


@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uid",
        "provider",
        "service",
        "access_level",
        "access_department",
        "access_location",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "provider",
        "service",
        "is_active",
        "access_level",
        "access_department",
        "access_location",
    )
    search_fields = (
        "id",
        "uid",
        "provider",
        "service",
        "api_key",
        "username",
        "client_id",
    )
    readonly_fields = ("uid", "created_at", "updated_at")

    ordering = ("-created_at",)
 