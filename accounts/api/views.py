from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView,
)

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from django.db.models import Q

#use pagination and permissions of Post app only
from blog.api.pagination import PostLimitOffsetPagination, PostPageNumberPagination
from blog.api.permissions import IsOwnerOrReadOnly

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser ,
    IsAuthenticatedOrReadOnly,
)
from blog.api.permissions import IsOwnerOrReadOnly
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from .serializers import *

User = get_user_model()


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            return Response(new_data, HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


