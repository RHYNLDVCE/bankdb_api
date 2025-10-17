from rest_framework import serializers
from decimal import Decimal

class DepositSerializer(serializers.Serializer):
    """
    Serializer for the deposit action.
    """
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        min_value=Decimal('0.01') # Ensure amount is positive
    )