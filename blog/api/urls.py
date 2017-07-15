from django.conf.urls import url
from django.contrib import admin

from blog.api.views import (
    PostListAPIView,
    PostDetailAPIView,
    PostDeleteAPIView,
    PostUpdateAPIView,
    PostCreateAPIView,
    # CommentDetailAPIView,
    # CommentListAPIView
)

urlpatterns = [
    url(r'^$', PostListAPIView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', PostDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/delete$', PostDeleteAPIView.as_view(), name='delete'),
    url(r'^(?P<pk>\d+)/edit$', PostUpdateAPIView.as_view(), name='edit'),
    url(r'^create/$', PostCreateAPIView.as_view(), name='create'),
    # url(r'^(?P<pk>\d+)/comment/$', CommentDetailAPIView.as_view(), name='comment_detail'),
    # url(r'^comments$', CommentListAPIView.as_view(), name='comment_list')
]

