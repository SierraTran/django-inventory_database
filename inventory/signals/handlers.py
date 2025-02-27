from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from inventory.models import Item, ItemHistory


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
    changes = None
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


@receiver(post_delete, sender=Item)
def delete_item_history(sender, instance, **kwargs):
    """
    Creates an ItemHistory record when an item is deleted.

    Arguments:
        sender (Item): The model class that sent the signal.
        instance (Item): The instance of the model that is being deleted.
        **kwargs: Additional keyword arguments sent by the signal.
    """
    with transaction.atomic():  # Ensures atomicity
        ItemHistory.objects.create(
            item=instance, action="delete", user=instance.last_modified_by
        )
