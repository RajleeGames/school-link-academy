from django.db.models import Q
from django.shortcuts import render

from accounts.decorators import permission_required

from .models import AuditLog


@permission_required("audit.view")
def audit_log_list(request):
    query = request.GET.get("q", "").strip()
    action = request.GET.get("action", "").strip()
    app_label = request.GET.get("app", "").strip()
    model_name = request.GET.get("model", "").strip()

    logs = AuditLog.objects.select_related("user").all()

    if query:
        logs = logs.filter(
            Q(user__username__icontains=query)
            | Q(object_repr__icontains=query)
            | Q(message__icontains=query)
            | Q(ip_address__icontains=query)
            | Q(app_label__icontains=query)
            | Q(model_name__icontains=query)
        )

    if action:
        logs = logs.filter(action=action)

    if app_label:
        logs = logs.filter(app_label=app_label)

    if model_name:
        logs = logs.filter(model_name=model_name)

    app_labels = (
        AuditLog.objects.exclude(app_label="")
        .values_list("app_label", flat=True)
        .distinct()
        .order_by("app_label")
    )

    model_names = (
        AuditLog.objects.exclude(model_name="")
        .values_list("model_name", flat=True)
        .distinct()
        .order_by("model_name")
    )

    context = {
        "logs": logs[:500],
        "query": query,
        "action": action,
        "app_label": app_label,
        "model_name": model_name,
        "action_choices": AuditLog.ACTION_CHOICES,
        "app_labels": app_labels,
        "model_names": model_names,
    }

    return render(request, "audit/audit_log_list.html", context)