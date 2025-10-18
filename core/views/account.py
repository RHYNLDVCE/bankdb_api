from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from ..models import Account, Transaction
from ..serializers import (
    AccountSerializer, TransactionSerializer, DepositSerializer,
    WithdrawalSerializer, TransferSerializer
)

class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Account instances.
    """
    serializer_class = AccountSerializer

    def get_queryset(self):
        """
        This view should return a list of all the accounts
        for the currently authenticated user's customer profile.
        """
        user = self.request.user
        return Account.objects.filter(owner__user=user)

    def perform_create(self, serializer):
        """
        Automatically set the owner of the new account to the
        customer profile of the currently logged-in user.
        """
        # self.request.user.customer is available because of the OneToOneField
        serializer.save(owner=self.request.user.customer)

    @action(detail=True, methods=['post'], serializer_class=DepositSerializer)
    def deposit(self, request, pk=None):
        """
        Custom action to deposit money into an account.
        """
        account = self.get_object()
        serializer = self.get_serializer(data=request.data)
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

        if account.balance < amount:
            return Response(
                {'error': 'Insufficient funds.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            account.balance -= amount
            account.save()

            Transaction.objects.create(
                account=account,
                amount=amount,
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

        try:
            to_account = Account.objects.get(account_number=to_account_number)
        except Account.DoesNotExist:
            return Response({'error': 'Destination account not found.'}, status=status.HTTP_404_NOT_FOUND)

        if from_account == to_account:
            return Response({'error': 'Cannot transfer to the same account.'}, status=status.HTTP_400_BAD_REQUEST)

        if from_account.balance < amount:
            return Response({'error': 'Insufficient funds.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            from_account.balance -= amount
            from_account.save()

            Transaction.objects.create(
                account=from_account,
                amount=amount,
                transaction_type='TRANSFER',
                description=f'Transfer to {to_account.account_number}'
            )

            to_account.balance += amount
            to_account.save()

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
