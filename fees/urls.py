from django.urls import path
from . import views

urlpatterns = [
    path("", views.fees_home, name="fees_home"),

    path("categories/", views.fee_category_list, name="fee_category_list"),
    path("categories/<int:pk>/edit/", views.fee_category_update, name="fee_category_update"),
    path("categories/<int:pk>/delete/", views.fee_category_delete, name="fee_category_delete"),

    path("structures/", views.fee_structure_list, name="fee_structure_list"),
    path("structures/<int:pk>/edit/", views.fee_structure_update, name="fee_structure_update"),
    path("structures/<int:pk>/delete/", views.fee_structure_delete, name="fee_structure_delete"),

    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/create/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/edit/", views.invoice_update, name="invoice_update"),
    path("invoices/<int:pk>/delete/", views.invoice_delete, name="invoice_delete"),

    path("invoices/<int:pk>/items/add/", views.invoice_add_item, name="invoice_add_item"),
    path("invoices/items/<int:pk>/edit/", views.invoice_item_update, name="invoice_item_update"),
    path("invoices/items/<int:pk>/delete/", views.invoice_item_delete, name="invoice_item_delete"),

    path("debtors/", views.debtor_list, name="debtor_list"),

    path("payments/", views.payment_list, name="payment_list"),
    path("payments/student/<int:student_id>/", views.student_payment_history, name="student_payment_history"),
    path("payments/create/", views.payment_create, name="payment_create"),
    path("payments/<int:pk>/edit/", views.payment_update, name="payment_update"),
    path("payments/<int:pk>/delete/", views.payment_delete, name="payment_delete"),

    path("receipts/<int:pk>/", views.receipt_detail, name="receipt_detail"),
]