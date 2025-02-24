from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from inventory.models import Item, ItemHistory


# Regardless of being used or not, `**kwargs` needs to be included in the other parameters

@receiver(post_save, sender=Item)
def create_or_update_item_history(sender, instance, created, **kwargs):
    # TODO: Doc comment for `create_or_update_item_history`
    """
    _summary_

    Arguments:
        sender (): _description_
        instance (): _description_
        created (bool): _description_
    """
    action = "create" if created else "update"
    changes = None
    if not created:
        changes = []
        for field, change in instance.tracker.changed().items():
            old_value = change # `change` is the value that was changed, NOT the new value
            new_value = getattr(instance, field, None)
            changes.append(f"{field}: '{old_value}' has been changed to '{new_value}'")
        changes = ", ".join(changes)
    ItemHistory.objects.create(item=instance, action=action, user=instance.last_modified_by, changes=changes)



@receiver(post_delete, sender=Item)
def delete_item_history(sender, instance, **kwargs):
    # TODO: Doc comment for `delete_item_history`
    """
    _summary_

    Arguments:
        sender -- _description_
        instance -- _description_
    """
    ItemHistory.objects.create(
        item=instance, action="delete", user=instance.modified_by
    )
