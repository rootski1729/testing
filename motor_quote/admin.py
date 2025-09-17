from django.contrib import admin
from motor_quote.models import MotorQuoteRequest

@admin.register(MotorQuoteRequest)
class MotorQuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "name", "mongo_id", "created_at", "updated_at")
    search_fields = ("uid", "name", "mongo_id")
