from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView,
)

from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin

from .serializers import (
    CommentListSerializer,
    CommentDetailSerializer,
    create_comment_serializer,
    # CommentEditSerializer,
)
#use pagination and permissions of Post app only
from blog.api.pagination import PostLimitOffsetPagination, PostPageNumberPagination
from blog.api.permissions import IsOwnerOrReadOnly

from comments.models import Comment

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

from django.db.models import Q


class CommentCreateAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        model_type = self.request.GET.get("type")
        object_id = self.request.GET.get("object_id")
        parent_id = self.request.GET.get("parent_id", None)
        return create_comment_serializer(
            model_type=model_type,
            object_id=object_id,
            parent_id=parent_id,
            user=self.request.user,
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentListAPIView(ListAPIView):
    serializer_class = CommentListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user', 'content']
    pagination_class = PostPageNumberPagination
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        queryset = Comment.objects.filter(id__gte=0)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(user__icontains=query) |
                Q(content__icontains=query)
            ).distinct()
        return queryset


class CommentDetailAPIView(DestroyModelMixin, UpdateModelMixin, RetrieveAPIView):
    queryset = Comment.objects.filter(id__gte=0)
    # get all comments
    serializer_class = CommentDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def put(self, request, *args, **kwargs): # HTTP method
        return self.update(request, *args, **kwargs) # builtin method in UpdateModelMixin

    def delete(self, request, *args, **kwargs): # HTTP method
        return self.destroy(request, *args, **kwargs) # builtin method in DestroyModelMixin
