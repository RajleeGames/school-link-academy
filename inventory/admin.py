from django.contrib import admin

from .models import InventoryCategory, InventoryItem, StockIn, StockOut, Supplier


@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "contact_person", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "phone", "email", "contact_person")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "item_code",
        "category",
        "supplier",
        "quantity",
        "reorder_level",
        "unit",
        "status",
    )
    list_filter = ("category", "supplier", "status")
    search_fields = ("name", "item_code", "location")
    list_select_related = ("category", "supplier")


@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ("item", "quantity", "supplier", "buying_price", "received_date")
    list_filter = ("received_date", "supplier")
    search_fields = ("item__name", "item__item_code", "reference")
    list_select_related = ("item", "supplier")


@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display = ("item", "quantity", "purpose", "issued_to", "issued_date")
    list_filter = ("purpose", "issued_date")
    search_fields = ("item__name", "item__item_code", "issued_to", "reference")
    list_select_related = ("item",)