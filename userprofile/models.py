from django.db import models
from authentication.models import CustomUser
# Create your models here.
class Profile(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('followers_only', 'Followers Only'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=160, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    profile_visibility = models.CharField(choices=VISIBILITY_CHOICES,default='public')
    updated_at = models.DateTimeField(auto_now=True)
    website = models.URLField(null=True, blank=True)

    def can_view_profile(self, curr_user):
        if not curr_user.is_authenticated:
            return False
        
        if self.profile_visibility == 'public':
            return True
        
        if curr_user == self.user:
            return True
        
        if curr_user.is_staff:
            return True
        
        if self.profile_visibility == 'private':
            if self.profile_visibility == 'followers_only':
                return UserFollow.objects.filter(
                    follower=curr_user,
                    following=self.user
                ).exists()
            return False
    
    def update_stats(self):

        self.followers_count = UserFollow.objects.filter(
            following=self.user, 
            is_active=True
        ).count()
        
        self.following_count = UserFollow.objects.filter(
            follower=self.user, 
            is_active=True
        ).count()
        
        self.posts_count = Post.objects.filter(author=self.user).count()
        
        self.save(update_fields=['followers_count', 'following_count', 'posts_count'])
        
        
        
class UserFollow(models.Model):
    
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers_set')

    class Meta:
        unique_together = ('follower', 'following')

class Post(models.Model):
    pass