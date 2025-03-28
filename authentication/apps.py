from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    
    def ready(self):
        from django.db.models.signals import post_migrate

        post_migrate.connect(assign_permissions_to_groups, sender=self)

 
def get_permission(codename):
        from django.contrib.auth.models import Permission
        try:
            return Permission.objects.get(codename=codename)
        except Permission.DoesNotExist:
            print(f"\nPermission {codename} not found")
            return None   

    
def assign_permissions_to_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    # Define permissions and groups
    

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

    # Assign permissions to groups

    superuser_group = Group.objects.get(name="Superuser")
    superuser_group.permissions.add(
        add_user_permission, change_user_permission, delete_user_permission, view_user_permission,
        change_notification_permission, delete_notification_permission, view_notification_permission,
        add_item_permission, change_item_permission, delete_item_permission, view_item_permission,
        view_itemhistory_permission,
        view_itemrequest_permission,
        add_useditem_permission, change_useditem_permission, delete_useditem_permission, view_useditem_permission,
        add_purchaseorderitem_permission, change_purchaseorderitem_permission, delete_purchaseorderitem_permission, view_purchaseorderitem_permission,
    )

    technician_group = Group.objects.get(name="Technician")
    technician_group.permissions.add(
        change_notification_permission, delete_notification_permission, view_notification_permission,
        add_item_permission, change_item_permission, delete_item_permission, view_item_permission,
        view_itemhistory_permission,
        add_itemrequest_permission, change_itemrequest_permission, delete_itemrequest_permission, view_itemrequest_permission,
        add_useditem_permission, change_useditem_permission, delete_useditem_permission, view_useditem_permission,
        # No PurchaseOrderItem permissions
    )

    intern_group = Group.objects.get(name="Intern")
    intern_group.permissions.add(
        change_notification_permission, delete_notification_permission, view_notification_permission,
        change_item_permission, view_item_permission,
        view_itemhistory_permission,
        # No ItemRequest permissions
        # No UsedItem permissions
        # No PurchaseOrderItem permissions
    )

    viewer_group = Group.objects.get(name="Viewer")
    viewer_group.permissions.add(
        change_notification_permission, delete_notification_permission, view_notification_permission,
        view_item_permission,
        view_itemhistory_permission,
        # No ItemRequest permissions
        # No UsedItem permissions
        # No PurchaseOrderItem permissions
    )
    
    
