from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from ..models import Customer

class RegistrationSerializer(serializers.ModelSerializer):
    # These fields are for input only
    full_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)
    gender = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'full_name', 
            'phone_number', 'date_of_birth', 'gender'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        phone_number = validated_data.pop('phone_number')
        date_of_birth = validated_data.pop('date_of_birth')
        gender = validated_data.pop('gender')
        user = User.objects.create_user(**validated_data)
        
        Customer.objects.create(
            user=user,
            full_name=full_name,
            email=user.email,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            gender=gender
        )
        
        return user