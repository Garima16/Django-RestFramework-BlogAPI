from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView,
)
from .serializers import (
    PostListSerializer,
    # PostDetailSerializer,
    PostCreateSerializer,
    post_detail_serializer
    # CommentListSerializer
)

from blog.models import Post

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser ,
    IsAuthenticatedOrReadOnly,
)
from .pagination import PostLimitOffsetPagination, PostPageNumberPagination

from .permissions import IsOwnerOrReadOnly
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)

from django.db.models import Q


class PostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'text']
    pagination_class = PostPageNumberPagination
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        queryset = Post.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(text__icontains=query)
            ).distinct()
        return queryset


class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    # serializer_class = PostDetailSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        return post_detail_serializer(self.request)


class PostUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
        # email(can send mail to the user who last updated the post)


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsOwnerOrReadOnly]


class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
