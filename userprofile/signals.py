from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from .models import Like, Comment, UserFollow

@receiver(post_save, sender=UserFollow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.following,  
            sender=instance.follower,
            notification_type='follow',
            message=f"{instance.follower.username} started following you"
        )

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='like',
            post=instance.post,
            message=f"{instance.user.username} liked your post"
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='comment',
            post=instance.post,
            message=f"{instance.user.username} commented on your post"
        )
