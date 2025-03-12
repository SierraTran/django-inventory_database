from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils.html import escape
from inventory.models import Item, ItemHistory, ItemRequest, UsedItem
from authentication.models import Notification


# Regardless of being used or not, `**kwargs` needs to be included in the other parameters


@receiver(post_save, sender=Item)
def create_or_update_item_history(sender, instance, created, **kwargs):
    """
    Creates an ItemHistory record when an item has been created or updated.

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
    Deletes records related to the item being deleted before its own deletion.

    Arguments:
        sender (Item): The model class that sent the signal.
        instance (Item): The instance of the model that's being deleted.
        **kwargs: Additional keyword arguments sent by the signal.
    """
    ItemHistory.objects.filter(item=instance).delete()
    UsedItem.objects.filter(item=instance).delete()
    
# TODO: Signals that create notifications
@receiver(post_save, sender=ItemRequest)
def send_item_request_notification(sender, instance, created, **kwargs):
    """
    Creates a notification for Technicians if their item request has been accepted or rejected.

    Args:
        sender (ItemRequest): The model class that sent the signal.
        instance (ItemRequest): The instance of the model that has been accepted or rejected.
        created (bool): True if the action done onto the item is "create", False if otherwise.
        **kwargs: Additional keyword arguments sent by the signal.
    """
    if created:
        # No notification is needed for an item request being created (at least not yet).
        return
    else: 
        subject = escape(f"Item Request {instance.status}")
        
        item_request_url = reverse("inventory:item_request_detail", kwargs={"pk": instance.pk})
        linked_item_request = f'<a href="{item_request_url}">Your Item Request for {instance.manufacturer}, {instance.model_part_num}</a>'
        
        message = escape(f"{linked_item_request} has been {str(instance.status).lower()}.")
    with transaction.atomic():
        Notification.objects.create(
            is_read=False,
            subject=subject,
            message=message,
            user=instance.requested_by,
        )

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
        
        item_url = reverse("inventory:item_detail", kwargs={"pk": instance.pk})
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