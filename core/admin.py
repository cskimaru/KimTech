from django.contrib import admin

from .models import ContactMessage, EngagementModel, Package, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary")


@admin.register(EngagementModel)
class EngagementModelAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "price_description", "is_featured", "order", "is_published")
    list_editable = ("order", "is_published", "is_featured")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "service_interest", "is_read", "created_at")
    list_editable = ("is_read",)
    list_filter = ("service_interest", "is_read", "created_at")
    search_fields = ("name", "email", "company", "message")
    readonly_fields = ("name", "email", "company", "phone", "service_interest", "message", "created_at")
