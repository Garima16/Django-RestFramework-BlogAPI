from rest_framework.serializers import (ModelSerializer,
                                        HyperlinkedIdentityField,
                                        SerializerMethodField,
                                        ValidationError,
                                        EmailField,
                                        CharField,
                                        )

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]


class UserCreateSerializer(ModelSerializer):
    email = EmailField(label='Email address')
    # overrides default nature of email being an optional field while user registration,now it's a
    # mandatory field

    email2 = EmailField(label='Confirm Email address')

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'email2',
            'password',
        ]

        extra_kwargs = {
            "password":{
                "write_only": True
            }
        }

    def validate(self, data):
        email = data['email']
        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            raise ValidationError('A user with this email has already been registered.')
        return data

    def validate_email2(self, value): # raise a validation error only for email2 field
        data = self.get_initial() # get initially filled data,whether validated or not
        email1 = data.get("email")
        email2 = value
        if email1 != email2:
            raise ValidationError('Emails donot match!')

        return value

    def create(self, validated_data):
        print "%s" % validated_data
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data['email']
        user_obj = User(
            username=username,
            email=email
        )
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class UserLoginSerializer(ModelSerializer):
    token = CharField(allow_blank=True, read_only=True)
    username = CharField(required=False, allow_blank=True)
    email = EmailField(label='Email address', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'token',
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate(self, data):
        email = data.get("email", None) # if email not found,set default email=None
        username = data.get("username", None)
        password = data['password'] # sure that password key exists in data
        if not email and not username:
            raise ValidationError('Username or email is required to login')
        user = User.objects.filter(
            Q(email=email) |
            Q(username=username)
        ).distinct()
        user = user.exclude(email__isnull=True).exclude(email__iexact='')
        print "%s" % user
        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError('Invalid username or email.')
        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError("Incorrect Password")
        data["token"] = "SOME RANDOM TOKEN"
        return data
