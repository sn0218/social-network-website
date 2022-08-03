from tkinter import CASCADE
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self):
        return f"User id: {self.id} | Username: {self.username}"

    def get_username(self):
        return self.username


# define the model of a post
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_post", verbose_name="Posted by")
    headline = models.CharField(max_length=128)
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Posted on")
    
    def __str__(self):
        return f"Post id: {self.id} | Posted by: {self.user} | Headline: {self.headline}"

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "headline": self.headline,
            "content": self.content,
            "timestamp": self.date.strftime("%b %d %Y, %I:%M %p")
        }


# define the model of comment
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment", verbose_name="Commented by")
    message = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Commented on")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comment")

    def __str__(self):
        return f"Comment id: {self.id} | {self.user} commented on {self.post}."
    
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "post": self.post.id,
            "message": self.message,
            "timestamp": self.date.strftime("%b %d %Y, %I:%M %p")
        }



# define the model of like
class Like(models.Model):
    """ Store all the like info """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like", verbose_name="Liked by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like")

    def __str__(self):
        return f"Like id: {self.id} | {self.user.username} liked {self.post.id}."


# define the model of following
class Following(models.Model):
    """
    Store the following info 
    user: the user who is following another user
    followed_user: the user who is being followed

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")

    def __str__(self):
        return f"{self.user} is following {self.followed_user}."
