import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    def get_permission(codename):
        try:
            return Permission.objects.get(codename=codename)
        except Permission.DoesNotExist:
            return None

    # Permissions for the User model
    add_user_permission = get_permission("add_user")
    change_user_permission = get_permission("change_user")
    delete_user_permission = get_permission("delete_user")
    view_user_permission = get_permission("view_user")

    # Permissions for the Notification model
    change_notification_permission = get_permission("change_notification")
    delete_notification_permission = get_permission("delete_notification")
    view_notification_permission = get_permission("view_notification")

    # Permissions for the Item model
    add_item_permission = get_permission("add_item")
    change_item_permission = get_permission("change_item")
    delete_item_permission = get_permission("delete_item")
    view_item_permission = get_permission("view_item")

    # Permissions for the ItemHistory model
    view_itemhistory_permission = get_permission("view_itemhistory")

    # Permissions for the ItemRequest model
    add_itemrequest_permission = get_permission("add_itemrequest")
    change_itemrequest_permission = get_permission("change_itemrequest")
    delete_itemrequest_permission = get_permission("delete_itemrequest")
    view_itemrequest_permission = get_permission("view_itemrequest")

    # Permissions for the UsedItem model
    add_useditem_permission = get_permission("add_useditem")
    change_useditem_permission = get_permission("change_useditem")
    delete_useditem_permission = get_permission("delete_useditem")
    view_useditem_permission = get_permission("view_useditem")

    # Permissions for the PurchaseOrderItem model
    add_purchaseorderitem_permission = get_permission("add_purchaseorderitem")
    change_purchaseorderitem_permission = get_permission("change_purchaseorderitem")
    delete_purchaseorderitem_permission = get_permission("delete_purchaseorderitem")
    view_purchaseorderitem_permission = get_permission("view_purchaseorderitem")

    # Create user groups and assign permissions to groups
    if not Group.objects.filter(name="Superuser").exists():
        superuser_group = Group.objects.create(name="Superuser")
        superuser_group.permissions.add(
            # User (object) permissions
            add_user_permission,
            change_user_permission,
            delete_user_permission,
            view_user_permission,
            # Notification permissions
            change_notification_permission,
            delete_notification_permission,
            view_notification_permission,
            # Item permissions
            add_item_permission,
            change_item_permission,
            delete_item_permission,
            view_item_permission,
            # ItemHistory permissions
            view_itemhistory_permission,
            # ItemRequest permissions
            view_itemrequest_permission,
            # UsedItem permissions
            add_useditem_permission,
            change_useditem_permission,
            delete_useditem_permission,
            view_useditem_permission,
            # PurchaseOrderItem permissions
            add_purchaseorderitem_permission,
            change_purchaseorderitem_permission,
            delete_purchaseorderitem_permission,
            view_purchaseorderitem_permission,
        )

    if not Group.objects.filter(name="Technician").exists():
        technician_group = Group.objects.create(name="Technician")
        technician_group.permissions.add(
            # Notification permissions
            change_notification_permission,
            delete_notification_permission,
            view_notification_permission,
            # Item permissions
            add_item_permission,
            change_item_permission,
            delete_item_permission,
            view_item_permission,
            # ItemHistory permissions
            view_itemhistory_permission,
            # ItemRequest permissions
            add_itemrequest_permission,
            change_itemrequest_permission,
            delete_itemrequest_permission,
            view_itemrequest_permission,
            # UsedItem permissions
            add_useditem_permission,
            change_useditem_permission,
            delete_useditem_permission,
            view_useditem_permission,
        )

    if not Group.objects.filter(name="Intern").exists():
        intern_group = Group.objects.create(name="Intern")
        intern_group.permissions.add(
            # Notification permissions
            change_notification_permission,
            delete_notification_permission,
            view_notification_permission,
            # Item permissions
            change_item_permission,
            view_item_permission,
            # ItemHistory permissions
            view_itemhistory_permission,
        )

    if not Group.objects.filter(name="Viewer").exists():
        viewer_group = Group.objects.create(name="Viewer")
        viewer_group.permissions.add(
            # Notification permissions
            change_notification_permission,
            delete_notification_permission,
            view_notification_permission,
            # Item permissions
            view_item_permission,
            # ItemHistory permissions
            view_itemhistory_permission,
        )


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ("authentication", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
