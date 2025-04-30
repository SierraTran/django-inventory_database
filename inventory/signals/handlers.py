"""
This module contains signal handlers for the Inventory app.

Imported Signals
    - post_save: Sent after a model's `save` method is called.
    - pre_delete: Sent just before a model's `delete` method is called.
"""

from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.utils.html import escape
from inventory.models import Item, ItemHistory, ItemRequest, UsedItem
from authentication.models import Notification

# NOTE: Regardless of being used or not, `sender` and `**kwargs` parameters need to be included in
# the other signal handlers to avoid errors.


@receiver(post_save, sender=Item)
def create_or_update_item_history(sender, instance, created, **kwargs):
    """
    Creates an ItemHistory record when an item has been created or updated.
    
    This method first checks if the item has been created or updated. If the item has been created,
    the action is set to "create". If the item has been updated, the action is set to "update". The
    changes are then recorded in a newly created ItemHistory record. Records with the "update"
    action will have the fields that have been changed and their old values recorded in the 
    `changes` field.

    Arguments:
        sender (Item): The model class that sent the signal.
        instance (Item): The instance of the model that's being created or updated.
        created (bool): True if the action done onto the item is "create", False if otherwise.
        **kwargs: Additional keyword arguments sent by the signal.
    """

    action = "create" if created else "update"
    changes = "Created and added to the database."
    if not created:
        changes = []
        for field, change in instance.tracker.changed().items():
            old_value = (
                change  # 'change' is the old value before the update, not the new value
            )
            new_value = getattr(instance, field, None)
            changes.append(f"{field}: '{old_value}' has been changed to '{new_value}'")
        changes = ", ".join(changes)
    with transaction.atomic():
        ItemHistory.objects.create(
            item=instance,
            action=action,
            user=instance.last_modified_by,
            changes=changes,
        )

@receiver(pre_delete, sender=Item)
def handle_related_records(sender, instance, **kwargs):
    """
    Deletes all records related to the item being deleted before its own deletion.

    Arguments:
        sender (Item): The model class that sent the signal.
        instance (Item): The instance of the model that's being deleted.
        **kwargs: Additional keyword arguments sent by the signal.
    """
    ItemHistory.objects.filter(item=instance).delete()
    # QUESTION: Delete this line and make UsedItem not directly reference the item so it can stay in the database?
    UsedItem.objects.filter(item=instance).delete()
    
# NOTE: The following signal handlers create notifications for users when certain events happen in 
# they system.
@receiver(post_save, sender=ItemRequest)
def send_item_request_notification(sender, instance, created, **kwargs):
    """ 
    Creates a notification for Technicians if their item request has been accepted or rejected by a
    Superuser, or creates a notification for Superusers if a new item request has been created.
    
    This method checks if the item request is created or not. If it is, a notification is created
    for all Superusers. If the item request is not created, it checks if the status of the item
    request has changed. If it has, a notification is created for the user that requested the item.

    Args:
        sender (ItemRequest): The model class that sent the signal.
        instance (ItemRequest): The instance of the model that has been accepted or rejected.
        created (bool): True if the action done onto the item is "create", False if otherwise.
        **kwargs: Additional keyword arguments sent by the signal.
    """
    subject = None
    message = None
    user = None
    instance_url = instance.get_absolute_url()

    if created:
        subject = "New Item Request"
        message = f"There's a new item request for {instance.manufacturer}, {instance.model_part_num}. " \
                    f'See the <a href="{instance_url}">item request</a> for more details.'
        superuser_group = Group.objects.get(name="Superuser")        
        for user in superuser_group.user_set.all():
            Notification.objects.create(
                is_read=False,
                subject=subject,
                message=message,
                user=user,
            )
        return

    if 'status' in instance.tracker.changed(): 
        # Display the new status of the item request in the subject of the notification.
        subject = escape(f"Item Request {instance.status}")
        # Create a link to the item request to include in the message.
        linked_item_request = f'<a href="{instance_url}">Your Item Request for {instance.manufacturer}, {instance.model_part_num}</a>'
        # Explain the new status of the item request and include its link in the message.
        message = f"{linked_item_request} has been {str(instance.status).lower()} by {instance.status_changed_by.username}. " \
                    "If you're all set with your item request, please delete it."
        with transaction.atomic():
            Notification.objects.create(
                is_read=False,
                subject=subject,
                message=message,
                user=instance.requested_by,
            )
        return

@receiver(post_save, sender=Item)
def send_low_stock_notification(sender, instance, **kwargs):
    """
    Creates a notification for all Superusers if an item is low in stock and how many are left.
    A new notification for this is created everytime the item is used.

    Args:
        sender (Item): The model class that sent the signal.
        instance (Item): The instance of the model that has been accepted or rejected.
        **kwargs: Additional keyword arguments sent by the signal.
    """
    if instance.low_stock:
        subject = "Low Stock Alert"
        item_url = instance.get_absolute_url()
        linked_item = f'<a href="{item_url}">{instance}</a>'
        message = f"{linked_item} is low in stock. {instance.quantity} left."
        superuser_group = Group.objects.get(name="Superuser")

        for user in superuser_group.user_set.all():
            Notification.objects.create(
                is_read=False,
                subject=subject,
                message=message,
                user=user,
            )
