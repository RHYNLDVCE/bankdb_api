# core/views/account.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from ..models import Account, Transaction
from ..serializers import AccountSerializer
from ..serializers import TransactionSerializer
from ..serializers import DepositSerializer
from ..serializers import WithdrawalSerializer
from ..serializers import TransferSerializer

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer

    def get_queryset(self):
            """
            This view should return a list of all the accounts
            for the currently authenticated user's customer profile.
            """
            user = self.request.user
            return Account.objects.filter(owner__user=user)

    @action(detail=True, methods=['post'], serializer_class=DepositSerializer) # <-- Tell DRF about the serializer
    def deposit(self, request, pk=None):
        """
        Custom action to deposit money into an account.
        """
        account = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        # Use the serializer's validation
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        with transaction.atomic():
            account.balance += amount
            account.save()

            Transaction.objects.create(
                account=account,
                amount=amount,
                transaction_type='DEPOSIT',
                description=f'Deposit of {amount} to account {account.account_number}.'
            )

        return Response(
            {'status': 'deposit successful', 'new_balance': account.balance},
            status=status.HTTP_200_OK
        )
    

    @action(detail=True, methods=['post'], serializer_class=WithdrawalSerializer)
    def withdraw(self, request, pk=None):
        """
        Custom action to withdraw money from an account.
        """
        account = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']

        # --- CRITICAL: Business Logic Validation ---
        if account.balance < amount:
            return Response(
                {'error': 'Insufficient funds.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Atomic Transaction ---
        with transaction.atomic():
            # 1. Update account balance
            account.balance -= amount
            account.save()

            # 2. Create transaction record
            Transaction.objects.create(
                account=account,
                amount=amount, # Store the positive amount of the withdrawal
                transaction_type='WITHDRAWAL',
                description=f'Withdrawal of {amount} from account {account.account_number}.'
            )

        return Response(
            {'status': 'withdrawal successful', 'new_balance': account.balance},
            status=status.HTTP_200_OK
        )
    

    @action(detail=True, methods=['post'], serializer_class=TransferSerializer)
    def transfer(self, request, pk=None):
        """
        Custom action to transfer money from one account to another.
        """
        from_account = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_account_number = serializer.validated_data['to_account_number']
        amount = serializer.validated_data['amount']

        # --- Business Logic Validation ---
        try:
            to_account = Account.objects.get(account_number=to_account_number)
        except Account.DoesNotExist:
            return Response({'error': 'Destination account not found.'}, status=status.HTTP_404_NOT_FOUND)

        if from_account == to_account:
            return Response({'error': 'Cannot transfer to the same account.'}, status=status.HTTP_400_BAD_REQUEST)

        if from_account.balance < amount:
            return Response({'error': 'Insufficient funds.'}, status=status.HTTP_400_BAD_REQUEST)

        # --- THE ATOMIC TRANSACTION ---
        with transaction.atomic():
            # 1. Debit the source account
            from_account.balance -= amount
            from_account.save()

            # 2. Create withdrawal transaction record for the source account
            Transaction.objects.create(
                account=from_account,
                amount=amount,
                transaction_type='TRANSFER',
                description=f'Transfer to {to_account.account_number}'
            )

            # 3. Credit the destination account
            to_account.balance += amount
            to_account.save()

            # 4. Create deposit transaction record for the destination account
            Transaction.objects.create(
                account=to_account,
                amount=amount,
                transaction_type='TRANSFER',
                description=f'Transfer from {from_account.account_number}'
            )

        return Response(
            {'status': 'transfer successful', 'from_account_balance': from_account.balance},
            status=status.HTTP_200_OK
        )