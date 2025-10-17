# core/views/customer.py
from rest_framework import viewsets
from ..models import Customer
from ..serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user = self.request.user
        return Customer.objects.filter(user=user)