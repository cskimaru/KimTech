from django.contrib import admin

from .models import (
    ContactMessage,
    Order,
    EngagementModel,
    Package,
    Partner,
    PartnerBenefit,
    Service,
)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("category", "is_published")
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
    list_filter = ("status",)
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
    list_display = ("name", "category", "partner", "price_description", "is_featured", "order", "is_published")
    list_editable = ("order", "is_published", "is_featured")
    list_filter = ("category", "partner")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "service_interest", "is_read", "created_at")
    list_editable = ("is_read",)
    list_filter = ("service_interest", "is_read", "created_at")
    search_fields = ("name", "email", "company", "message")
    readonly_fields = ("name", "email", "company", "phone", "service_interest", "message", "created_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "phone", "services_display", "domain_name", "status", "mpesa_code", "amount_quoted", "created_at")
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    search_fields = ("reference", "name", "email", "phone", "domain_name", "mpesa_code")
    readonly_fields = ("reference", "order_page", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("reference", "status", "amount_quoted", "mpesa_code", "order_page")}),
        ("What they ordered", {"fields": ("package", "services", "domain_name", "notes")}),
        ("Customer", {"fields": ("name", "email", "phone", "company")}),
        ("Internal", {"fields": ("internal_notes", "created_at", "updated_at")}),
    )

    @admin.display(description="Services")
    def services_display(self, obj):
        return ", ".join(obj.service_labels())

    @admin.display(description="Customer's order page")
    def order_page(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html

        if not obj.pk:
            return "-"
        url = reverse("order_detail", kwargs={"token": obj.token})
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a> (send this link to the customer if they lose it)', url, url)
