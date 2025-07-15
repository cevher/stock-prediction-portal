from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
        
    def create(self, validated_data):
        # Create a new user instance
        # user = User.objects.create_user(**validated_data)
        # User.objects.create = save the password in a plain text and it needs to be hashed
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        user.save()
        return user