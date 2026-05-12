from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import permission_required

from audit.utils import log_audit, model_to_dict_safe

from .forms import (
    InventoryCategoryForm,
    InventoryItemForm,
    StockInForm,
    StockOutForm,
    SupplierForm,
)
from .models import InventoryCategory, InventoryItem, StockIn, StockOut, Supplier


def safe_delete_object(request, obj, success_message, redirect_url):
    old_values = model_to_dict_safe(obj)
    app_label = obj._meta.app_label
    model_name = obj._meta.model_name
    object_id = str(obj.pk)
    object_repr = str(obj)

    try:
        obj.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted {model_name}: {object_repr}",
            old_values=old_values,
        )

        messages.success(request, success_message)

    except ProtectedError:
        messages.error(
            request,
            "This record cannot be deleted because it is already used somewhere. You can edit it or mark it inactive instead."
        )

    except Exception:
        messages.error(
            request,
            "This record could not be deleted. Please check if it is connected to other records."
        )

    return redirect(redirect_url)


def apply_stock_in(stock_in):
    item = stock_in.item
    item.quantity += stock_in.quantity

    if stock_in.buying_price and stock_in.buying_price > 0:
        item.buying_price = stock_in.buying_price

    if stock_in.supplier:
        item.supplier = stock_in.supplier

    item.save()


def reverse_stock_in(stock_in):
    item = stock_in.item

    if stock_in.quantity > item.quantity:
        return False

    item.quantity -= stock_in.quantity
    item.save()
    return True


def apply_stock_out(stock_out):
    item = stock_out.item

    if stock_out.quantity > item.quantity:
        return False

    item.quantity -= stock_out.quantity
    item.save()
    return True


def reverse_stock_out(stock_out):
    item = stock_out.item
    item.quantity += stock_out.quantity
    item.save()
    return True


@permission_required("inventory.view")
def inventory_home(request):
    total_items = InventoryItem.objects.count()
    total_quantity = InventoryItem.objects.aggregate(total=Sum("quantity"))["total"] or 0
    low_stock_count = InventoryItem.objects.filter(quantity__lte=5).count()
    supplier_count = Supplier.objects.count()

    recent_stock_in = StockIn.objects.select_related("item", "supplier").order_by("-id")[:6]
    recent_stock_out = StockOut.objects.select_related("item").order_by("-id")[:6]

    categories = InventoryCategory.objects.annotate(
        item_count=Count("items")
    ).order_by("name")[:8]

    context = {
        "total_items": total_items,
        "total_quantity": total_quantity,
        "low_stock_count": low_stock_count,
        "supplier_count": supplier_count,
        "recent_stock_in": recent_stock_in,
        "recent_stock_out": recent_stock_out,
        "categories": categories,
    }

    return render(request, "inventory/home.html", context)


@permission_required("inventory.view")
def item_list(request):
    items = InventoryItem.objects.select_related("category", "supplier")

    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()
    stock = request.GET.get("stock", "").strip()

    if search:
        items = items.filter(
            Q(name__icontains=search)
            | Q(item_code__icontains=search)
            | Q(location__icontains=search)
            | Q(category__name__icontains=search)
            | Q(supplier__name__icontains=search)
        )

    if category_id:
        items = items.filter(category_id=category_id)

    if status:
        items = items.filter(status=status)

    if stock == "low":
        items = [item for item in items if item.is_low_stock]

    context = {
        "items": items,
        "categories": InventoryCategory.objects.filter(is_active=True),
        "search": search,
        "selected_category": category_id,
        "selected_status": status,
        "selected_stock": stock,
    }

    return render(request, "inventory/item_list.html", context)


@permission_required("inventory.manage")
def item_create(request):
    if request.method == "POST":
        form = InventoryItemForm(request.POST)

        if form.is_valid():
            item = form.save()

            log_audit(
                request,
                "create",
                obj=item,
                message=f"Created inventory item: {item}",
                new_values=model_to_dict_safe(item),
            )

            messages.success(request, "Inventory item added successfully.")
            return redirect("inventory_item_list")

        messages.error(request, "Please correct the item form.")

    else:
        form = InventoryItemForm()

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Add Inventory Item",
        "button_text": "Save Item",
        "back_url": "inventory_item_list",
    })


@permission_required("inventory.manage")
def item_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    old_values = model_to_dict_safe(item)

    if request.method == "POST":
        form = InventoryItemForm(request.POST, instance=item)

        if form.is_valid():
            updated_item = form.save()

            log_audit(
                request,
                "update",
                obj=updated_item,
                message=f"Updated inventory item: {updated_item}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_item),
            )

            messages.success(request, "Inventory item updated successfully.")
            return redirect("inventory_item_list")

        messages.error(request, "Please correct the item form.")

    else:
        form = InventoryItemForm(instance=item)

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Edit Inventory Item",
        "button_text": "Update Item",
        "back_url": "inventory_item_list",
    })


@permission_required("inventory.manage")
def item_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    if StockIn.objects.filter(item=item).exists() or StockOut.objects.filter(item=item).exists():
        messages.error(
            request,
            "This item has stock movement history. Do not delete it. Mark it inactive instead."
        )
        return redirect("inventory_item_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            item,
            "Inventory item deleted successfully.",
            "inventory_item_list"
        )

    return redirect("inventory_item_list")


@permission_required("inventory.view")
def category_list(request):
    categories = InventoryCategory.objects.annotate(item_count=Count("items"))

    search = request.GET.get("search", "").strip()

    if search:
        categories = categories.filter(name__icontains=search)

    return render(request, "inventory/category_list.html", {
        "categories": categories,
        "search": search,
    })


@permission_required("inventory.manage")
def category_create(request):
    if request.method == "POST":
        form = InventoryCategoryForm(request.POST)

        if form.is_valid():
            category = form.save()

            log_audit(
                request,
                "create",
                obj=category,
                message=f"Created inventory category: {category}",
                new_values=model_to_dict_safe(category),
            )

            messages.success(request, "Inventory category added successfully.")
            return redirect("inventory_category_list")

        messages.error(request, "Please correct the category form.")

    else:
        form = InventoryCategoryForm()

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Add Inventory Category",
        "button_text": "Save Category",
        "back_url": "inventory_category_list",
    })


@permission_required("inventory.manage")
def category_update(request, pk):
    category = get_object_or_404(InventoryCategory, pk=pk)
    old_values = model_to_dict_safe(category)

    if request.method == "POST":
        form = InventoryCategoryForm(request.POST, instance=category)

        if form.is_valid():
            updated_category = form.save()

            log_audit(
                request,
                "update",
                obj=updated_category,
                message=f"Updated inventory category: {updated_category}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_category),
            )

            messages.success(request, "Inventory category updated successfully.")
            return redirect("inventory_category_list")

        messages.error(request, "Please correct the category form.")

    else:
        form = InventoryCategoryForm(instance=category)

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Edit Inventory Category",
        "button_text": "Update Category",
        "back_url": "inventory_category_list",
    })


@permission_required("inventory.manage")
def category_delete(request, pk):
    category = get_object_or_404(InventoryCategory, pk=pk)

    if InventoryItem.objects.filter(category=category).exists():
        messages.error(
            request,
            "This category has items. Move those items to another category or mark this category inactive instead."
        )
        return redirect("inventory_category_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            category,
            "Inventory category deleted successfully.",
            "inventory_category_list"
        )

    return redirect("inventory_category_list")


@permission_required("inventory.view")
def supplier_list(request):
    suppliers = Supplier.objects.all()

    search = request.GET.get("search", "").strip()

    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
            | Q(contact_person__icontains=search)
        )

    return render(request, "inventory/supplier_list.html", {
        "suppliers": suppliers,
        "search": search,
    })


@permission_required("inventory.manage")
def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)

        if form.is_valid():
            supplier = form.save()

            log_audit(
                request,
                "create",
                obj=supplier,
                message=f"Created supplier: {supplier}",
                new_values=model_to_dict_safe(supplier),
            )

            messages.success(request, "Supplier added successfully.")
            return redirect("supplier_list")

        messages.error(request, "Please correct the supplier form.")

    else:
        form = SupplierForm()

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Add Supplier",
        "button_text": "Save Supplier",
        "back_url": "supplier_list",
    })


@permission_required("inventory.manage")
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    old_values = model_to_dict_safe(supplier)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)

        if form.is_valid():
            updated_supplier = form.save()

            log_audit(
                request,
                "update",
                obj=updated_supplier,
                message=f"Updated supplier: {updated_supplier}",
                old_values=old_values,
                new_values=model_to_dict_safe(updated_supplier),
            )

            messages.success(request, "Supplier updated successfully.")
            return redirect("supplier_list")

        messages.error(request, "Please correct the supplier form.")

    else:
        form = SupplierForm(instance=supplier)

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Edit Supplier",
        "button_text": "Update Supplier",
        "back_url": "supplier_list",
    })


@permission_required("inventory.manage")
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if InventoryItem.objects.filter(supplier=supplier).exists() or StockIn.objects.filter(supplier=supplier).exists():
        messages.error(
            request,
            "This supplier is already used in items or stock-in records. Mark it inactive instead."
        )
        return redirect("supplier_list")

    if request.method == "POST":
        return safe_delete_object(
            request,
            supplier,
            "Supplier deleted successfully.",
            "supplier_list"
        )

    return redirect("supplier_list")


@permission_required("inventory.view")
def stock_in_list(request):
    records = StockIn.objects.select_related("item", "supplier")

    search = request.GET.get("search", "").strip()

    if search:
        records = records.filter(
            Q(item__name__icontains=search)
            | Q(item__item_code__icontains=search)
            | Q(supplier__name__icontains=search)
            | Q(reference__icontains=search)
        )

    return render(request, "inventory/stock_in_list.html", {
        "records": records,
        "search": search,
    })


@permission_required("inventory.manage")
def stock_in_create(request):
    if request.method == "POST":
        form = StockInForm(request.POST)

        if form.is_valid():
            stock_in = form.save()
            item = stock_in.item
            old_item_values = model_to_dict_safe(item)

            apply_stock_in(stock_in)

            item.refresh_from_db()

            log_audit(
                request,
                "create",
                obj=stock_in,
                message=f"Created stock-in record: {stock_in}",
                new_values=model_to_dict_safe(stock_in),
            )

            log_audit(
                request,
                "update",
                obj=item,
                message=f"Item quantity increased by stock-in: {stock_in.quantity}.",
                old_values=old_item_values,
                new_values=model_to_dict_safe(item),
            )

            messages.success(request, "Stock in record saved successfully.")
            return redirect("stock_in_list")

        messages.error(request, "Please correct the stock in form.")

    else:
        form = StockInForm(initial={
            "received_date": timezone.localdate()
        })

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Add Stock In",
        "button_text": "Save Stock In",
        "back_url": "stock_in_list",
    })


@permission_required("inventory.manage")
def stock_in_update(request, pk):
    stock_in = get_object_or_404(StockIn.objects.select_related("item"), pk=pk)

    old_stock_in_values = model_to_dict_safe(stock_in)
    old_item = stock_in.item
    old_item_values_before_reverse = model_to_dict_safe(old_item)

    if request.method == "POST":
        old_stock_in = StockIn.objects.select_related("item").get(pk=pk)

        if not reverse_stock_in(old_stock_in):
            messages.error(
                request,
                "You cannot edit this stock-in because reversing the old quantity would make stock negative."
            )
            return redirect("stock_in_list")

        old_item.refresh_from_db()
        item_values_after_reverse = model_to_dict_safe(old_item)

        form = StockInForm(request.POST, instance=stock_in)

        if form.is_valid():
            updated_stock_in = form.save()
            new_item = updated_stock_in.item
            item_values_before_apply = model_to_dict_safe(new_item)

            apply_stock_in(updated_stock_in)

            new_item.refresh_from_db()

            log_audit(
                request,
                "update",
                obj=updated_stock_in,
                message=f"Updated stock-in record: {updated_stock_in}",
                old_values=old_stock_in_values,
                new_values=model_to_dict_safe(updated_stock_in),
            )

            log_audit(
                request,
                "update",
                obj=old_item,
                message=f"Reversed old stock-in quantity before update: {old_stock_in.quantity}.",
                old_values=old_item_values_before_reverse,
                new_values=item_values_after_reverse,
            )

            log_audit(
                request,
                "update",
                obj=new_item,
                message=f"Applied updated stock-in quantity: {updated_stock_in.quantity}.",
                old_values=item_values_before_apply,
                new_values=model_to_dict_safe(new_item),
            )

            messages.success(request, "Stock in record updated successfully.")
            return redirect("stock_in_list")

        apply_stock_in(old_stock_in)
        messages.error(request, "Please correct the stock in form.")

    else:
        form = StockInForm(instance=stock_in)

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Edit Stock In",
        "button_text": "Update Stock In",
        "back_url": "stock_in_list",
    })


@permission_required("inventory.manage")
def stock_in_delete(request, pk):
    stock_in = get_object_or_404(StockIn.objects.select_related("item"), pk=pk)

    old_stock_in_values = model_to_dict_safe(stock_in)
    app_label = stock_in._meta.app_label
    model_name = stock_in._meta.model_name
    object_id = str(stock_in.pk)
    object_repr = str(stock_in)

    item = stock_in.item
    old_item_values = model_to_dict_safe(item)

    if request.method == "POST":
        if not reverse_stock_in(stock_in):
            messages.error(
                request,
                "You cannot delete this stock-in because removing it would make item stock negative."
            )
            return redirect("stock_in_list")

        item.refresh_from_db()
        new_item_values = model_to_dict_safe(item)

        stock_in.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted stock-in record: {object_repr}",
            old_values=old_stock_in_values,
        )

        log_audit(
            request,
            "update",
            obj=item,
            message=f"Item quantity reduced after deleting stock-in: {object_repr}.",
            old_values=old_item_values,
            new_values=new_item_values,
        )

        messages.success(request, "Stock in record deleted successfully.")

    return redirect("stock_in_list")


@permission_required("inventory.view")
def stock_out_list(request):
    records = StockOut.objects.select_related("item")

    search = request.GET.get("search", "").strip()

    if search:
        records = records.filter(
            Q(item__name__icontains=search)
            | Q(item__item_code__icontains=search)
            | Q(issued_to__icontains=search)
            | Q(reference__icontains=search)
        )

    return render(request, "inventory/stock_out_list.html", {
        "records": records,
        "search": search,
    })


@permission_required("inventory.manage")
def stock_out_create(request):
    if request.method == "POST":
        form = StockOutForm(request.POST)

        if form.is_valid():
            stock_out = form.save(commit=False)
            item = stock_out.item
            old_item_values = model_to_dict_safe(item)

            if not apply_stock_out(stock_out):
                messages.error(request, "Insufficient stock.")
                return redirect("stock_out_create")

            stock_out.save()
            item.refresh_from_db()

            log_audit(
                request,
                "create",
                obj=stock_out,
                message=f"Created stock-out record: {stock_out}",
                new_values=model_to_dict_safe(stock_out),
            )

            log_audit(
                request,
                "update",
                obj=item,
                message=f"Item quantity reduced by stock-out: {stock_out.quantity}.",
                old_values=old_item_values,
                new_values=model_to_dict_safe(item),
            )

            messages.success(request, "Stock out record saved successfully.")
            return redirect("stock_out_list")

        messages.error(request, "Please correct the stock out form.")

    else:
        form = StockOutForm(initial={
            "issued_date": timezone.localdate()
        })

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Add Stock Out",
        "button_text": "Save Stock Out",
        "back_url": "stock_out_list",
    })


@permission_required("inventory.manage")
def stock_out_update(request, pk):
    stock_out = get_object_or_404(StockOut.objects.select_related("item"), pk=pk)

    old_stock_out_values = model_to_dict_safe(stock_out)
    old_item = stock_out.item
    old_item_values_before_reverse = model_to_dict_safe(old_item)

    if request.method == "POST":
        old_stock_out = StockOut.objects.select_related("item").get(pk=pk)

        reverse_stock_out(old_stock_out)

        old_item.refresh_from_db()
        item_values_after_reverse = model_to_dict_safe(old_item)

        form = StockOutForm(request.POST, instance=stock_out)

        if form.is_valid():
            updated_stock_out = form.save(commit=False)
            new_item = updated_stock_out.item
            item_values_before_apply = model_to_dict_safe(new_item)

            if not apply_stock_out(updated_stock_out):
                apply_stock_out(old_stock_out)

                messages.error(request, "Insufficient stock for the updated stock-out quantity.")
                return redirect("stock_out_update", pk=pk)

            updated_stock_out.save()
            new_item.refresh_from_db()

            log_audit(
                request,
                "update",
                obj=updated_stock_out,
                message=f"Updated stock-out record: {updated_stock_out}",
                old_values=old_stock_out_values,
                new_values=model_to_dict_safe(updated_stock_out),
            )

            log_audit(
                request,
                "update",
                obj=old_item,
                message=f"Reversed old stock-out quantity before update: {old_stock_out.quantity}.",
                old_values=old_item_values_before_reverse,
                new_values=item_values_after_reverse,
            )

            log_audit(
                request,
                "update",
                obj=new_item,
                message=f"Applied updated stock-out quantity: {updated_stock_out.quantity}.",
                old_values=item_values_before_apply,
                new_values=model_to_dict_safe(new_item),
            )

            messages.success(request, "Stock out record updated successfully.")
            return redirect("stock_out_list")

        apply_stock_out(old_stock_out)
        messages.error(request, "Please correct the stock out form.")

    else:
        form = StockOutForm(instance=stock_out)

    return render(request, "inventory/simple_form.html", {
        "form": form,
        "title": "Edit Stock Out",
        "button_text": "Update Stock Out",
        "back_url": "stock_out_list",
    })


@permission_required("inventory.manage")
def stock_out_delete(request, pk):
    stock_out = get_object_or_404(StockOut.objects.select_related("item"), pk=pk)

    old_stock_out_values = model_to_dict_safe(stock_out)
    app_label = stock_out._meta.app_label
    model_name = stock_out._meta.model_name
    object_id = str(stock_out.pk)
    object_repr = str(stock_out)

    item = stock_out.item
    old_item_values = model_to_dict_safe(item)

    if request.method == "POST":
        reverse_stock_out(stock_out)

        item.refresh_from_db()
        new_item_values = model_to_dict_safe(item)

        stock_out.delete()

        log_audit(
            request,
            "delete",
            app_label=app_label,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted stock-out record: {object_repr}",
            old_values=old_stock_out_values,
        )

        log_audit(
            request,
            "update",
            obj=item,
            message=f"Item quantity increased after deleting stock-out: {object_repr}.",
            old_values=old_item_values,
            new_values=new_item_values,
        )

        messages.success(request, "Stock out record deleted successfully.")

    return redirect("stock_out_list")