from rest_framework.serializers import (ModelSerializer,
                                        HyperlinkedIdentityField,
                                        SerializerMethodField,
                                        ValidationError,
                                        )

from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from accounts.api.serializers import UserDetailSerializer

User = get_user_model()


def create_comment_serializer(model_type='post', object_id=None, parent_id=None, user=None):
    class CommentCreateSerializer(ModelSerializer):
        class Meta:
            model = Comment
            fields = [
                'id',
                'content',
                # 'parent',
                'timestamp',
            ]

        def __init__(self, *args, **kwargs):
            self.model_type = model_type
            self.object_id = object_id
            self.parent_obj = None
            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id) # comment parent id
                if parent_qs.exists() and parent_qs.count() == 1:
                    self.parent_obj = parent_qs.first()
            return super(CommentCreateSerializer, self).__init__(*args, **kwargs)

        def validate(self, data): # taking data from __init__ method
            model_type = self.model_type
            model_qs = ContentType.objects.filter(model=model_type)
            if not model_qs.exists() or model_qs.count() != 1:
                raise ValidationError('not a valid content type')
            someModel = model_qs.first().model_class()
            # returns the model of the passed content_type-just to make sure that an instance of that particular
            # model exists, here someModel = Post ,importing the model without actually importing it :P,thus making
            # it dynamic or generic as using ContentType class
            obj_qs = someModel.objects.filter(id=self.object_id)
            # get the instance id of the passed content type model(here 'Post') instance
            if not obj_qs.exists() or obj_qs.count() != 1:
                raise ValidationError('not a valid id for this content type')
            return data

        def create(self, validated_data):
            content = validated_data.get('content')
            if user:
                main_user = user
            else:
                main_user = User.objects.all().first()
            model_type = self.model_type
            object_id = self.object_id
            parent_obj  =self.parent_obj
            comment = Comment.objects.create_by_model_type(
                content=content,
                user=main_user,
                model_type=model_type,
                id=object_id,
                parent_obj=parent_obj
            )
            return comment

    return CommentCreateSerializer


class CommentListSerializer(ModelSerializer):
    # url = HyperlinkedIdentityField(
    #     view_name='comments-api:thread',
    #     lookup_field='pk'
    # )
    reply_count = SerializerMethodField()
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            # 'url',
            'user',
            # 'content_type',
            # 'object_id',
            'content',
            # 'parent',
            'timestamp',
            'reply_count',

        ]

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.get_children().count()
        return 0


class CommentChildSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'content',
            'timestamp',
            'timestamp',
        ]


class CommentDetailSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    replies = SerializerMethodField()
    reply_count = SerializerMethodField()
    content_object_url = SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            # 'content_type',
            # 'object_id',
            'content',
            'replies',
            'timestamp',
            'reply_count',
            'content_object_url',
        ]

        read_only_fields = [
            # 'object_id',
            # 'content_type',
            'replies',
            'reply_count',
        ]

    def get_content_object_url(self, obj):
        try:
            return obj.content_object.get_api_url()
        except:
            return None

    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.get_children(), many=True).data
            # any queryset can be passed to above serializer even if it belongs to a completely different model
        return None

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.get_children().count()
        return 0


# class CommentEditSerializer(ModelSerializer):
#
#     class Meta:
#         model = Comment
#         fields = [
#             'id',
#             'content',
#             'timestamp',
#         ]
