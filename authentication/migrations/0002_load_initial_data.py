import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def load_initial_data(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # User groups
    superuser_group = Group.objects.create(name="Superuser")
    technician_group = Group.objects.create(name="Technician")
    intern_group = Group.objects.create(name="Intern")
    viewer_group = Group.objects.create(name="Viewer")

    # Permissions for the User model
    add_user_permission = Permission.objects.get(codename="add_user")
    change_user_permission = Permission.objects.get(codename="change_user")
    delete_user_permission = Permission.objects.get(codename="delete_user")
    view_user_permission = Permission.objects.get(codename="view_user")

    # Permissions for the Notification model
    view_notification_permission = Permission.objects.get(codename="view_notification")

    # Permissions for the Item model
    add_item_permission = Permission.objects.get(codename="add_item")
    change_item_permission = Permission.objects.get(codename="change_item")
    delete_item_permission = Permission.objects.get(codename="delete_item")
    view_item_permission = Permission.objects.get(codename="view_item")

    # Permissions for the ItemHistory model
    view_itemhistory_permission = Permission.objects.get(codename="view_itemhistory")

    # Permissions for the ItemRequest model
    add_itemrequest_permission = Permission.objects.get(codename="add_itemrequest")
    change_itemrequest_permission = Permission.objects.get(codename="change_itemrequest")
    delete_itemrequest_permission = Permission.objects.get(codename="delete_itemrequest")
    view_itemrequest_permission = Permission.objects.get(codename="view_itemrequest")

    # Permissions for the UsedItem model
    add_useditem_permission = Permission.objects.get(codename="add_useditem")
    change_useditem_permission = Permission.objects.get(codename="change_useditem")
    delete_useditem_permission = Permission.objects.get(codename="delete_useditem")
    view_useditem_permission = Permission.objects.get(codename="view_useditem")

    # Permissions for the PurchaseOrderItem model
    add_purchaseorderitem_permission = Permission.objects.get(codename="add_purchaseorderitem")
    change_purchaseorderitem_permission = Permission.objects.get(codename="change_purchaseorderitem")
    delete_purchaseorderitem_permission = Permission.objects.get(codename="delete_purchaseorderitem")
    view_purchaseorderitem_permission = Permission.objects.get(codename="view_purchaseorderitem")

    # Assign permissions to groups
    superuser_group.permissions.add(
        add_user_permission, change_user_permission, delete_user_permission, view_user_permission,
        view_notification_permission,
        add_item_permission, change_item_permission, delete_item_permission, view_item_permission,
        view_itemhistory_permission,
        view_itemrequest_permission,
        add_useditem_permission, change_useditem_permission, delete_useditem_permission, view_useditem_permission,
        add_purchaseorderitem_permission, change_purchaseorderitem_permission, delete_purchaseorderitem_permission, view_purchaseorderitem_permission,
    )
    technician_group.permissions.add(
        view_notification_permission,
        add_item_permission, change_item_permission, delete_item_permission, view_item_permission,
        view_itemhistory_permission,
        add_itemrequest_permission, change_itemrequest_permission, delete_itemrequest_permission, view_itemrequest_permission,
        add_useditem_permission, change_useditem_permission, delete_useditem_permission, view_useditem_permission,
        # No PurchaseOrderItem permissions
    )
    intern_group.permissions.add(
        view_notification_permission,
        change_item_permission, view_item_permission,
        view_itemhistory_permission,
        # No ItemRequest permissions
        # No UsedItem permissions
        # No PurchaseOrderItem permissions
    )
    viewer_group.permissions.add(
        view_notification_permission,
        view_item_permission,
        view_itemhistory_permission,
        # No ItemRequest permissions
        # No UsedItem permissions
        # No PurchaseOrderItem permissions
    )


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ("authentication", "0001_initial"),
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
