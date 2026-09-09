from django.contrib import admin

from .models import (
    ContactMessage,
    EngagementModel,
    Package,
    Partner,
    PartnerBenefit,
    Service,
)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary")


class PartnerBenefitInline(admin.TabularInline):
    model = PartnerBenefit
    extra = 1


class EngagementModelInline(admin.TabularInline):
    model = EngagementModel
    extra = 1


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "one_liner")
    inlines = [PartnerBenefitInline, EngagementModelInline]


@admin.register(EngagementModel)
class EngagementModelAdmin(admin.ModelAdmin):
    list_display = ("name", "partner", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("partner",)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "partner", "price_description", "is_featured", "order", "is_published")
    list_editable = ("order", "is_published", "is_featured")
    list_filter = ("partner",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "service_interest", "is_read", "created_at")
    list_editable = ("is_read",)
    list_filter = ("service_interest", "is_read", "created_at")
    search_fields = ("name", "email", "company", "message")
    readonly_fields = ("name", "email", "company", "phone", "service_interest", "message", "created_at")
