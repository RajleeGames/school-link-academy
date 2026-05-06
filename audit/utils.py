from .models import AuditLog


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def log_audit(
    request,
    action,
    obj=None,
    message="",
    old_values=None,
    new_values=None,
    app_label="",
    model_name="",
    object_id="",
    object_repr="",
):
    user = None

    if request and request.user.is_authenticated:
        user = request.user

    if obj:
        meta = obj._meta
        app_label = app_label or meta.app_label
        model_name = model_name or meta.model_name
        object_id = object_id or str(obj.pk)
        object_repr = object_repr or str(obj)

    AuditLog.objects.create(
        user=user,
        action=action,
        app_label=app_label,
        model_name=model_name,
        object_id=object_id,
        object_repr=object_repr,
        message=message,
        old_values=old_values or {},
        new_values=new_values or {},
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
    )


def model_to_dict_safe(obj, fields=None):
    data = {}

    if not obj:
        return data

    model_fields = obj._meta.fields

    for field in model_fields:
        name = field.name

        if fields and name not in fields:
            continue

        value = getattr(obj, name, None)

        if hasattr(value, "pk"):
            value = str(value)

        data[name] = str(value) if value is not None else ""

    return data