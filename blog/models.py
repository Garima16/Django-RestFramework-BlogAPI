from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User


def upload_location(post, filename):
    return "%s/%s" % (post.id, filename)


class PostManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(PostManager, self).filter(published_date__lte=timezone.now())
        # Post.objects.all()= super(PostManager, self).all()


class Post(models.Model):
    user = models.ForeignKey(User, default=1)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True,
                              upload_to=upload_location,
                              height_field="height_field",
                              width_field="width_field")
    height_field = models.IntegerField(default=0, null=True)
    width_field = models.IntegerField(default=0, null=True)
    is_favorite = models.BooleanField(default=False)
    # id = models.IntegerField()
    objects = PostManager() # link each Post object with PostManager so that it's methods can be used with each object
    # default convention to use 'objects' in Django,can use any other variable as well, then instead of using
    # Post.objects.all, use Post.<variable>.all

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def get_api_url(self):
        return reverse("posts-api:detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

