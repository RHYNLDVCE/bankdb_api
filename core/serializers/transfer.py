from rest_framework import serializers
from decimal import Decimal

class TransferSerializer(serializers.Serializer):
    """
    Serializer for the transfer action.
    """
    to_account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        min_value=Decimal('0.01')
    )