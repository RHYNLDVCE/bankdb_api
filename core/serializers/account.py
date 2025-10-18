from rest_framework import serializers
from ..models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        # Explicitly list the fields
        fields = [
            'id', 'owner', 'account_number', 'account_type',
            'balance', 'created_at', 'updated_at'
        ]
        # Make owner and account_number read-only. They will be shown in responses,
        # but cannot be set or changed by the user in a request.
        read_only_fields = ['owner', 'account_number']
