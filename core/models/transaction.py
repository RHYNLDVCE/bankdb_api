# core/models/transaction.py
from django.db import models
from .account import Account

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    )

    # The account this transaction belongs to.
    # on_delete=models.PROTECT prevents an account from being deleted if it has transactions,
    # which is crucial for maintaining a complete and accurate audit trail.
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    
    # The amount of the transaction. We use DecimalField for financial accuracy.
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # The type of the transaction, using the predefined choices.
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    
    # The exact time the transaction was recorded. This is set automatically on creation.
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # An optional note or description for the transaction.
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for account {self.account.account_number}"