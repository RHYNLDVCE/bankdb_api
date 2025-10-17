from django.db import models
from .customer import Customer 
import random
import time

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('SAVINGS', 'Savings'),
        ('CHECKING', 'Checking'),
    )
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.full_name} - {self.account_type} ({self.account_number})"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.account_number = f"ACC-{int(time.time())}{random.randint(100, 999)}"
        super().save(*args, **kwargs)