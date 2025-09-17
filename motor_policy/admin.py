from django.contrib import admin

from .models import MotorPolicy


@admin.register(MotorPolicy)
class MotorPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "uid", 
        "name", 
        "company", 
        "access_department", 
        "access_location",
        "mongo_id",
        "is_active",
        "created_at"
    )
    search_fields = (
        "id", 
        "uid", 
        "name", 
        "mongo_id",
        "company__name", 
        "company__uid",
        "access_department__name",
        "access_department__uid",
        "access_location__name",
        "access_location__uid"
    )
    list_filter = (
        "is_active",
        "company",
        "access_department",
        "access_location",
        "created_at",
        "updated_at"
    )
    readonly_fields = (
        "uid",
        "created_at",
        "updated_at"
    )
    filter_horizontal = ("owners",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
