from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import *


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'identifier'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    lookup_field = 'phone_number'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

    @action(detail=False, methods=['delete'], url_path='delete-by-user')
    def update_by_user(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = self.request.query_params.dict()

        try:
            instance = queryset.get(**filter_kwargs)
        except State.DoesNotExist:
            return Response({"error": "Resource not found"}, status=status.HTTP_404_NOT_FOUND)

        instance.delete()

        return Response({"message": "Resource deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class StateViewSet(ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

    @action(detail=False, methods=['patch'], url_path='update-by-user')
    def update_by_user(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = self.request.query_params.dict()

        try:
            instance = queryset.get(**filter_kwargs)
        except State.DoesNotExist:
            return Response({"error": "Resource not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
