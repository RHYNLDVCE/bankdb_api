from rest_framework import viewsets
from ..models import Transaction
from ..serializers import TransactionSerializer

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__owner__user=user)