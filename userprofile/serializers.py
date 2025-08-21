from rest_framework import serializers
from .models import Profile, UserFollow, Comment, Post

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
    post_count = serializers.IntegerField(read_only=True)
    
    is_following = serializers.SerializerMethodField()
    is_follower = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'first_name', 'last_name', 'last_active',
            'bio', 'avatar', 'website', 'profile_visibility',
            'followers_count', 'following_count', 'post_count',
            'is_following', 'is_follower'
        ]
        read_only_fields = [
            'username', 'email', 'first_name', 'last_name', 'last_active', 'followers_count', 
            'following_count', 'post_count', 'is_following', 'is_follower'
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

class UserFollowSerializer(serializers.ModelSerializer):
    follower = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=UserFollow.objects.all(),
                fields=['follower', 'following'],
                message="You are already following this user."
            )
        ]

class ProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    class Meta:
        model = Profile
        fields = ['id', 'username', 'first_name', 'last_name', 'bio', 'avatar']

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'author_username', 'created_at']
        read_only_fields = ['user']

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='user.username', read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'content', 'user', 'author_username', 'created_at', 'updated_at', 
                 'image_url', 'category', 'like_count', 'comment_count', 'is_liked']
        read_only_fields = ['user', 'like_count', 'comment_count']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False