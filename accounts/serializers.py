from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, CustomerProfile, TravelsProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone', 'first_name', 'last_name')
        read_only_fields = ('id',)


class CustomerSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'phone', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        password2 = validated_data.pop('password2')
        password = validated_data.pop('password')
        validated_data['user_type'] = 'customer'
        
        # Handle phone number - can be empty string
        if 'phone' in validated_data and not validated_data['phone']:
            validated_data['phone'] = None
            
        user = User.objects.create_user(password=password, **validated_data)
        CustomerProfile.objects.create(user=user)
        return user


class TravelsSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'phone', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        password2 = validated_data.pop('password2')
        password = validated_data.pop('password')
        validated_data['user_type'] = 'travels'
        validated_data['is_staff'] = True  # Grant admin access to travel users
        
        # Handle phone number - can be empty string
        if 'phone' in validated_data and not validated_data['phone']:
            validated_data['phone'] = None
            
        user = User.objects.create_user(password=password, **validated_data)
        TravelsProfile.objects.create(user=user)
        return user

