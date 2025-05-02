"""
This module contains context processors for the authentication app.
"""

from .models import Notification

def unread_notifications_count(request):
    """
    Context processor to count unread notifications for the authenticated user.
    
    This function checks if the user is authenticated and counts the number of unread
    notifications associated with the user. It returns a dictionary containing the number
    of unread notifications, which can be accessed in templates. If the user is not authenticated,
    it returns a count of 0.
    
    Returns:
        dict: A dictionary containing the count of unread notifications under the key
              'unread_notifications_count'.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
