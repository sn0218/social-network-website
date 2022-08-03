
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:name>", views.profile, name="profile"),
    path("following", views.following, name="following"),

    # API routes
    path("post", views.composePost, name="composePost"),
    path("posts", views.getAllPosts, name="displayPost"),
    path("posts/<int:post_id>", views.getPost, name="getPost"),
    path("edit/<int:post_id>", views.editPost, name="editPost"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("followerCount/<str:name>", views.followerCount, name="followerCount"),
    path("like/<int:post_id>", views.like, name="like"),
    path("likeCount/<int:post_id>", views.likeCount, name="likeCount")
]
