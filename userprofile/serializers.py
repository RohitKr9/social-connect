from rest_framework import serializers
from .models import Profile, UserFollow

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    last_active = serializers.DateTimeField(source='user.last_active', read_only=True)
   
    bio = serializers.CharField(max_length=160, required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    profile_visibility = serializers.ChoiceField(choices=Profile.VISIBILITY_CHOICES,default='public')
    
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    
    is_following = serializers.SerializerMethodField()
    is_follower = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'first_name', 'last_name', 'last_active',
            'bio', 'avatar', 'website', 'profile_visibility',
            'followers_count', 'following_count', 'posts_count',
            'is_following', 'is_follower'
        ]
        read_only_fields = [
            'username', 'email', 'first_name', 'last_name', 'last_active', 'followers_count', 
            'following_count', 'posts_count', 'is_following', 'is_follower'
        ]

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        
        if request.user == obj.user:
            return False  
        
        return UserFollow.objects.filter(
            follower=request.user,
            following=obj.user
        ).exists()

    def get_is_follower(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        
        if request.user == obj.user:
            return False
        
        return UserFollow.objects.filter(
            follower=obj.user,
            following=request.user
        ).exists()

