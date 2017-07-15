from rest_framework.serializers import (ModelSerializer,
                                        HyperlinkedIdentityField,
                                        SerializerMethodField,
                                        ValidationError
                                        )

from blog.models import Post
from comments.api.serializers import CommentListSerializer, CommentDetailSerializer
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from accounts.api.serializers import UserDetailSerializer


class PostCreateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'author',
            'published_date',
        ]


class PostListSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='posts-api:detail',
        lookup_field='pk',
    )
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'url',
            'id',
            'title',
            'text',
            'user',
        ]


def post_detail_serializer(request):

    class PostDetailSerializer(ModelSerializer):
        comments = SerializerMethodField()
        user = UserDetailSerializer(read_only=True)
        image = SerializerMethodField()
        delete_url = HyperlinkedIdentityField(
            view_name='posts-api:delete',
            lookup_field='pk',
        )

        class Meta:
            model = Post
            fields = [
                'delete_url',
                'title',
                'text',
                'user',
                'published_date',
                'image',
                'comments',
            ]

        def get_image(self, obj):
            try:
                image = obj.image.url
            except:
                image = None
            return image

        def get_comments(self, obj):
            c_qs = Comment.objects.filter_by_instance(obj)
            comments = CommentListSerializer(
                c_qs, 
                many=True,
                context={'request': request}
            ).data
            return comments
    return PostDetailSerializer